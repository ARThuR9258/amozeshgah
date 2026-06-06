from pathlib import Path

from quizbuilder_module.pdf_import.parse_questions import (
    merge_short_options,
    normalize_block_layout,
    parse_questions_from_text,
)

raw = Path('data/import/isargaran82_raw.txt').read_text(encoding='utf-8')
chunk = raw.split('--- PAGE 35 ---')[1].split('--- PAGE')[0]
norm = normalize_block_layout(chunk)
qs = parse_questions_from_text(norm, page=35)
merged = merge_short_options(qs)
out = Path('data/import/debug_parse.txt')
lines = [f'{len(qs)} parsed', f'{len(merged)} merged']
for q in qs[:8]:
    filled = sum(1 for o in (q.option1, q.option2, q.option3, q.option4) if len(o) >= 2)
    lines.append(f'n={q.number} filled={filled} qlen={len(q.question)}')
out.write_text('\n'.join(lines), encoding='utf-8')
print(out.read_text(encoding='utf-8'))
