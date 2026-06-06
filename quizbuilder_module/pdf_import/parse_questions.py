from __future__ import annotations

import re
from dataclasses import dataclass, field

from .utils import clean_text, normalize_digits

# شماره سوال معمولاً در خط جدا و خط بعد «-» دارد (نه گزینه 1 تا 4)
QUESTION_START = re.compile(
    r'(?:^|\n)\s*(\d{1,3})\s*\n\s*[-–—]\s*',
    re.MULTILINE,
)


def normalize_options_layout(text: str) -> str:
    """فقط گزینه‌های 1 تا 4: «1\\n-\\nمتن» → «1- متن»."""
    text = re.sub(r'([1-4])\s*\n\s*[-–—]\s*', r'\n\1- ', text)
    text = re.sub(r'([1-4])\s*\n\s*\)\s*', r'\n\1) ', text)
    return text

OPTION_PATTERNS = [
  # 1) متن  2) متن
    re.compile(
        r'(?:^|\s)([1-4])\s*[\)）]\s*([^1-4]{2,}?)(?=(?:\s[2-4]\s*[\)）])|$)',
        re.DOTALL,
    ),
    # 1( متن  2( متن  (پرانتز فارسی)
    re.compile(
        r'([1-4])\s*[\(（]\s*([^1-4]{2,}?)(?=\s*[2-4]\s*[\(（]|$)',
        re.DOTALL,
    ),
    # خطوط 1- گزینه
    re.compile(
        r'(?:^|\n)\s*([1-4])\s*[-–—]\s*([^\n]+)',
        re.MULTILINE,
    ),
]

ANSWER_KEY_LINE = re.compile(
    r'(?:^|\n)\s*(\d{1,3})\s*[-–:]\s*([1-4])\s*(?:\n|$)',
    re.MULTILINE,
)


@dataclass
class ParsedQuestion:
    number: int | None
    question: str
    option1: str = ''
    option2: str = ''
    option3: str = ''
    option4: str = ''
    correct_answer: str = ''
    question_image: str = ''
    page: int | None = None
    raw_block: str = ''
    warnings: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict:
        return {
            'question': self.question,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_answer': self.correct_answer,
            'question_image': self.question_image,
        }


def _extract_options(block: str) -> dict[int, str]:
    opts: dict[int, str] = {}
    for pattern in OPTION_PATTERNS:
        for m in pattern.finditer(block):
            num = int(m.group(1))
            txt = re.sub(r'\s+', ' ', m.group(2)).strip(' .،؛:')
            if len(txt) >= 2 and (num not in opts or len(txt) > len(opts[num])):
                opts[num] = txt
        if len(opts) >= 4:
            break
    return opts


def _strip_options_from_question(block: str, opts: dict[int, str]) -> str:
    q = block
    q = QUESTION_START.sub('', q, count=1)
    for pattern in OPTION_PATTERNS:
        q = pattern.sub(' ', q)
    q = re.sub(r'گزینه\s*[1-4]', ' ', q)
    q = re.sub(r'\s+', ' ', q).strip(' -–—؟?.')
    return q


def parse_answer_key(text: str) -> dict[int, int]:
    answers: dict[int, int] = {}
    for m in ANSWER_KEY_LINE.finditer(normalize_digits(text)):
        answers[int(m.group(1))] = int(m.group(2))
    return answers


def _is_number_only(line: str) -> bool:
    return bool(re.match(r'^\d{1,3}$', line))


def _is_marker_start(lines: list[str], idx: int) -> bool:
    if idx + 1 >= len(lines) or not _is_number_only(lines[idx]):
        return False
    nxt = lines[idx + 1]
    return nxt.startswith('-') or nxt == '-' or nxt.startswith('–') or nxt.startswith('—')


def _read_marker_block(lines: list[str], idx: int) -> tuple[str, int]:
    """بعد از خط شماره، متن بعد از '-' تا شروع بلوک بعدی."""
    parts: list[str] = []
    if idx < len(lines):
        first = lines[idx]
        if first.startswith(('-', '–', '—')):
            rest = first.lstrip('-–—').strip()
            if rest:
                parts.append(rest)
            idx += 1
    while idx < len(lines) and not _is_marker_start(lines, idx):
        if lines[idx]:
            parts.append(lines[idx])
        idx += 1
    return re.sub(r'\s+', ' ', ' '.join(parts)).strip(), idx


def split_question_blocks(text: str) -> list[tuple[int | None, str]]:
    """
    پارس خط‌به‌خط: تمایز شماره سوال از گزینه 1–4.
    """
    text = clean_text(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    blocks: list[tuple[int | None, str]] = []
    current_q: int | None = None
    current_q_text = ''
    opts: dict[int, str] = {}

    def flush_question() -> None:
        nonlocal current_q, current_q_text, opts
        if current_q is None or len(current_q_text) < 5:
            return
        body = current_q_text
        for n in range(1, 5):
            if n in opts:
                body += f'\n{n}- {opts[n]}'
        blocks.append((current_q, body))
        current_q = None
        current_q_text = ''
        opts = {}

    i = 0
    while i < len(lines):
        if not _is_marker_start(lines, i):
            i += 1
            continue
        num = int(lines[i])
        i += 1
        content, i = _read_marker_block(lines, i)

        if num in (1, 2, 3, 4) and current_q is not None and len(opts) < 4:
            if content:
                opts[num] = content
            continue

        flush_question()
        current_q = num
        current_q_text = content
        opts = {}

    flush_question()
    return blocks


def parse_questions_from_text(
    text: str,
    *,
    page: int | None = None,
    page_images: list[str] | None = None,
    answer_key: dict[int, int] | None = None,
) -> list[ParsedQuestion]:
    results: list[ParsedQuestion] = []
    for num, block in split_question_blocks(text):
        if num is None:
            continue
        block = normalize_options_layout(block)
        opts = _extract_options(block)
        q_text = _strip_options_from_question(block, opts)
        if len(q_text) < 8:
            continue
        pq = ParsedQuestion(
            number=num,
            question=q_text,
            option1=opts.get(1, ''),
            option2=opts.get(2, ''),
            option3=opts.get(3, ''),
            option4=opts.get(4, ''),
            page=page,
            raw_block=block[:500],
        )
        if answer_key and num in answer_key:
            pq.correct_answer = str(answer_key[num])
        needs_image = any(
            k in block for k in ('شکل', 'شکل مقابل', 'در این شکل', 'نشان داده')
        )
        if needs_image and page_images:
            pq.question_image = page_images[0]
        if not pq.option1 and not pq.option2:
            pq.warnings.append('options_not_found')
        results.append(pq)
    return results


def parse_document(
    page_texts: list[str],
    page_images: dict[int, list[str]] | None = None,
    answer_key_text: str = '',
    *,
    start_page: int = 1,
) -> list[ParsedQuestion]:
    answer_key = parse_answer_key(answer_key_text) if answer_key_text else {}
    all_q: list[ParsedQuestion] = []
    seen: set[tuple[str, str]] = set()

    for idx, text in enumerate(page_texts):
        if not (text or '').strip():
            continue
        page_num = start_page + idx
        imgs = (page_images or {}).get(page_num, [])
        for pq in parse_questions_from_text(
            text,
            page=page_num,
            page_images=imgs,
            answer_key=answer_key,
        ):
            key = (pq.question[:60], pq.option1[:30])
            if key in seen:
                continue
            seen.add(key)
            all_q.append(pq)

    return all_q


def merge_short_options(questions: list[ParsedQuestion]) -> list[ParsedQuestion]:
    """حداقل اعتبارسنجی کیفیت."""
    cleaned: list[ParsedQuestion] = []
    for q in questions:
        filled = sum(1 for o in (q.option1, q.option2, q.option3, q.option4) if len(o) >= 2)
        if filled >= 2 and len(q.question) >= 10:
            cleaned.append(q)
        elif filled >= 1 and len(q.question) >= 20:
            cleaned.append(q)
    return cleaned
