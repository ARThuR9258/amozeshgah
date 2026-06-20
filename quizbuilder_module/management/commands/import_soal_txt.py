"""
وارد کردن سوالات آزمون از فایل متنی soal.txt

سوالاتی که شامل (توصیف تصویر: ...) هستند وارد نمی‌شوند.

اجرا:
  python manage.py import_soal_txt --file "C:\\Users\\...\\soal.txt"
"""
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quizbuilder_module.models import Category, Question

PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
OPTION_SPLIT_RE = re.compile(r'([۱۲۳۴])\)\s*')
QUESTION_LINE_RE = re.compile(r'^سوال\s+[۰-۹\d]+:\s*')
ANSWER_RE = re.compile(r'پاسخ\s*صحیح:\s*گزینه\s+([۱۲۳۴\d]+)')
IMAGE_DESC_MARKER = '(توصیف تصویر:'


def persian_to_int(value: str) -> int:
    return int(value.strip().translate(PERSIAN_DIGITS))


def parse_question_line(line: str) -> dict | None:
    """یک خط سوال را پارس می‌کند؛ در صورت خطا None."""
    ans_match = ANSWER_RE.search(line)
    if not ans_match:
        return None

    correct = persian_to_int(ans_match.group(1))
    if correct not in (1, 2, 3, 4):
        return None

    body = line[:ans_match.start()].strip()
    body = QUESTION_LINE_RE.sub('', body)

    parts = OPTION_SPLIT_RE.split(body)
    if len(parts) < 9:
        return None

    question_text = parts[0].strip()
    options = [parts[i].strip().rstrip('.') for i in (2, 4, 6, 8)]

    if not question_text or any(not opt for opt in options):
        return None

    return {
        'text': question_text,
        'option_1': options[0],
        'option_2': options[1],
        'option_3': options[2],
        'option_4': options[3],
        'correct_answer': correct,
    }


class Command(BaseCommand):
    help = 'Import exam questions from soal.txt (skips image-description questions)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=r'C:\Users\Lenovo T570\Desktop\soal.txt',
            help='مسیر فایل سوالات',
        )
        parser.add_argument(
            '--category',
            default='ayin-nameh',
            help='slug دسته‌بندی',
        )
        parser.add_argument(
            '--category-name',
            default='آیین‌نامه',
            help='نام دسته در صورت ایجاد',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='فقط گزارش بدون ذخیره',
        )
        parser.add_argument(
            '--clear-category',
            action='store_true',
            help='حذف سوالات قبلی همین دسته قبل از import',
        )

    def handle(self, *args, **options):
        file_path = Path(options['file']).expanduser().resolve()
        if not file_path.exists():
            raise CommandError(f'File not found: {file_path}')

        content = file_path.read_text(encoding='utf-8')
        if 'راهنمای تصاویر' in content:
            content = content.split('راهنمای تصاویر')[0]

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith('سوال')
        ]

        category, _ = Category.objects.get_or_create(
            slug=options['category'],
            defaults={'name': options['category_name'], 'is_active': True},
        )

        skipped_image = 0
        skipped_parse = 0
        to_import: list[dict] = []

        for line in lines:
            if IMAGE_DESC_MARKER in line:
                skipped_image += 1
                continue
            parsed = parse_question_line(line)
            if not parsed:
                skipped_parse += 1
                continue
            to_import.append(parsed)

        self.stdout.write(f'Total lines: {len(lines)}')
        self.stdout.write(f'Skipped (image description): {skipped_image}')
        self.stdout.write(f'Skipped (parse error): {skipped_parse}')
        self.stdout.write(f'Ready to import: {len(to_import)}')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run — nothing saved.'))
            return

        with transaction.atomic():
            if options['clear_category']:
                deleted, _ = Question.objects.filter(category=category).delete()
                self.stdout.write(f'Deleted {deleted} old questions in category.')

            created = 0
            for item in to_import:
                if Question.objects.filter(text=item['text'], category=category).exists():
                    continue
                Question.objects.create(
                    category=category,
                    is_active=True,
                    **item,
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Imported {created} questions into category slug={category.slug}'
            )
        )
