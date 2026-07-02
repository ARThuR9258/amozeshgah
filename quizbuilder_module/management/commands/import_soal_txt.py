"""
وارد کردن سوالات آزمون از فایل متنی soal.txt

هر «آزمون شماره N» یک دسته‌بندی جدا می‌شود (slug: azmon-N).

اجرا:
  python manage.py import_soal_txt --file "C:\\Users\\...\\soal.txt"
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quizbuilder_module.models import Category, Question

PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
EXAM_HEADER_RE = re.compile(r'^آزمون\s+شماره\s+([۰-۹\d]+)\s*$', re.MULTILINE)
QUESTION_START_RE = re.compile(r'(?:^|\s)([۰-۹\d]{1,2})[-.]\s*')
OPTION_SPLIT_RE = re.compile(r'([۱۲۳۴])\)\s*')
PAGE_REF_RE = re.compile(r'\s*\[[۰-۹\d،\s]+\]\s*$')
SKIP_MARKERS = (
    '(توصیف تصویر:',
    '(گزینه‌های ۱ تا ۴)',
    '(اشاره به تصاویر',
)


def persian_to_int(value: str) -> int:
    return int(value.strip().translate(PERSIAN_DIGITS))


def split_exam_sections(content: str) -> list[tuple[int, str]]:
    """متن فایل را به بخش‌های آزمون تقسیم می‌کند."""
    matches = list(EXAM_HEADER_RE.finditer(content))
    if not matches:
        return []

    sections = []
    for i, match in enumerate(matches):
        exam_num = persian_to_int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]
        sections.append((exam_num, body))
    return sections


def split_questions(exam_body: str) -> list[str]:
    """بخش یک آزمون را به بلوک‌های سوال تقسیم می‌کند."""
    exam_body = re.sub(r'_{5,}', '\n', exam_body)
    exam_body = re.sub(r'\n{3,}', '\n\n', exam_body)

    chunks: list[str] = []
    for line in exam_body.splitlines():
        line = line.strip()
        if not line or line.startswith('بخش '):
            continue

        starts = list(QUESTION_START_RE.finditer(line))
        if not starts:
            continue

        for idx, match in enumerate(starts):
            q_start = match.start(1) if match.start(1) == 0 else match.start()
            q_end = starts[idx + 1].start() if idx + 1 < len(starts) else len(line)
            chunk = line[q_start:q_end].strip()
            if chunk:
                chunks.append(chunk)

    return chunks


def parse_question_block(block: str) -> dict | None:
    """یک بلوک سوال را پارس می‌کند."""
    if any(marker in block for marker in SKIP_MARKERS):
        return None

    block = QUESTION_START_RE.sub('', block, count=1).strip()
    block = PAGE_REF_RE.sub('', block).strip()

    parts = OPTION_SPLIT_RE.split(block)
    if len(parts) < 9:
        return None

    question_text = parts[0].strip().rstrip('.')
    options = [parts[i].strip().rstrip('.') for i in (2, 4, 6, 8)]

    if not question_text or any(not opt for opt in options):
        return None

    # فایل فعلاً پاسخ صحیح ندارد — پیش‌فرض گزینه ۱ (بعداً در پنل اصلاح شود)
    return {
        'text': question_text,
        'option_1': options[0],
        'option_2': options[1],
        'option_3': options[2],
        'option_4': options[3],
        'correct_answer': 1,
    }


class Command(BaseCommand):
    help = 'Import exam questions from soal.txt into per-exam categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=r'C:\Users\Lenovo T570\Desktop\soal.txt',
            help='مسیر فایل سوالات',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='فقط گزارش بدون ذخیره',
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='حذف همه سوالات و دسته‌بندی‌های آزمون (azmon-*) قبل از import',
        )

    def handle(self, *args, **options):
        file_path = Path(options['file']).expanduser().resolve()
        if not file_path.exists():
            raise CommandError(f'File not found: {file_path}')

        content = file_path.read_text(encoding='utf-8')
        sections = split_exam_sections(content)
        if not sections:
            raise CommandError('هیچ بخش «آزمون شماره» در فایل پیدا نشد.')

        stats = {
            'exams': 0,
            'imported': 0,
            'skipped': 0,
            'duplicates': 0,
        }
        exam_details: list[str] = []

        parsed_by_exam: dict[int, list[dict]] = {}
        for exam_num, body in sections:
            parsed_by_exam[exam_num] = []
            for block in split_questions(body):
                item = parse_question_block(block)
                if item:
                    parsed_by_exam[exam_num].append(item)
                else:
                    stats['skipped'] += 1

        for exam_num in sorted(parsed_by_exam):
            count = len(parsed_by_exam[exam_num])
            exam_details.append(f'  آزمون {exam_num}: {count} سوال')
            stats['imported'] += count

        stats['exams'] = len(parsed_by_exam)

        self.stdout.write(f'Exams found: {stats["exams"]}')
        self.stdout.write(f'Questions ready: {stats["imported"]}')
        self.stdout.write(f'Skipped (no options / image): {stats["skipped"]}')
        for line in exam_details:
            self.stdout.write(line)

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run — nothing saved.'))
            return

        with transaction.atomic():
            if options['clear_all']:
                exam_cats = Category.objects.filter(slug__startswith='azmon-')
                q_deleted, _ = Question.objects.filter(category__in=exam_cats).delete()
                c_deleted, _ = exam_cats.delete()
                self.stdout.write(f'Cleared {q_deleted} questions, {c_deleted} categories.')

            for exam_num in sorted(parsed_by_exam):
                slug = f'azmon-{exam_num}'
                category, _ = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': f'آزمون {exam_num}',
                        'is_active': True,
                        'display_order': exam_num,
                    },
                )
                if category.name != f'آزمون {exam_num}':
                    category.name = f'آزمون {exam_num}'
                    category.display_order = exam_num
                    category.is_active = True
                    category.save(update_fields=['name', 'display_order', 'is_active'])

                created = 0
                for item in parsed_by_exam[exam_num]:
                    if Question.objects.filter(text=item['text'], category=category).exists():
                        stats['duplicates'] += 1
                        continue
                    Question.objects.create(category=category, is_active=True, **item)
                    created += 1

                self.stdout.write(f'  → {slug}: {created} سوال جدید')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {stats["imported"] - stats["duplicates"]} questions imported '
                f'into {stats["exams"]} categories.'
            )
        )
        if stats['duplicates']:
            self.stdout.write(f'Duplicates skipped: {stats["duplicates"]}')
        self.stdout.write(
            self.style.WARNING(
                'توجه: فایل پاسخ صحیح ندارد — correct_answer فعلاً روی گزینه ۱ است. '
                'از پنل مدیریت اصلاح کنید.'
            )
        )
