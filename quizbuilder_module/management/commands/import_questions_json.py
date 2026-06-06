"""
وارد کردن سوالات از JSON به مدل Question.

مثال:
  python manage.py import_questions_json ^
    --json data/import/isargaran82_questions.json ^
    --category ayin-nameh ^
    --images-base data/import/isargaran82_images
"""
import json
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quizbuilder_module.models import Category, Question


class Command(BaseCommand):
    help = 'Import questions from JSON file into Question model'

    def add_arguments(self, parser):
        parser.add_argument('--json', required=True, help='مسیر فایل JSON')
        parser.add_argument(
            '--category',
            default='ayin-nameh',
            help='slug دسته‌بندی (در صورت نبود ساخته می‌شود)',
        )
        parser.add_argument(
            '--category-name',
            default='آیین‌نامه',
            help='نام فارسی دسته در صورت ایجاد',
        )
        parser.add_argument(
            '--images-base',
            default='',
            help='پوشه پایه برای مسیرهای question_image در JSON',
        )
        parser.add_argument(
            '--difficulty',
            default='medium',
            choices=['easy', 'medium', 'hard'],
            help='سطح سختی پیش‌فرض',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='فقط گزارش بدون ذخیره',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='اگر سوالی با همان متن وجود داشت، به‌روزرسانی شود',
        )

    def handle(self, *args, **options):
        json_path = Path(options['json']).expanduser().resolve()
        if not json_path.exists():
            raise CommandError(f'JSON not found: {json_path}')

        try:
            items = json.loads(json_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON: {exc}') from exc

        if not isinstance(items, list):
            raise CommandError('JSON root must be an array')

        images_base = Path(options['images_base']).resolve() if options['images_base'] else None

        category, _ = Category.objects.get_or_create(
            slug=options['category'],
            defaults={
                'name': options['category_name'],
                'is_active': True,
            },
        )

        created = updated = skipped = 0

        @transaction.atomic
        def run():
            nonlocal created, updated, skipped
            for idx, row in enumerate(items, start=1):
                if not isinstance(row, dict):
                    skipped += 1
                    continue
                q_text = (row.get('question') or row.get('text') or '').strip()
                if len(q_text) < 5:
                    skipped += 1
                    continue

                o1 = (row.get('option1') or row.get('option_1') or '').strip()
                o2 = (row.get('option2') or row.get('option_2') or '').strip()
                o3 = (row.get('option3') or row.get('option_3') or '').strip()
                o4 = (row.get('option4') or row.get('option_4') or '').strip()

                if not o1:
                    o1 = 'گزینه ۱'
                if not o2:
                    o2 = 'گزینه ۲'
                if not o3:
                    o3 = 'گزینه ۳'
                if not o4:
                    o4 = 'گزینه ۴'

                correct_raw = row.get('correct_answer') or row.get('correct') or ''
                try:
                    correct = int(str(correct_raw).strip() or 0)
                except ValueError:
                    correct = 0
                if correct not in (1, 2, 3, 4):
                    correct = 1

                defaults = {
                    'text': q_text,
                    'option_1': o1[:500],
                    'option_2': o2[:500],
                    'option_3': o3[:500],
                    'option_4': o4[:500],
                    'correct_answer': correct,
                    'category': category,
                    'difficulty': options['difficulty'],
                    'is_active': True,
                }

                existing = Question.objects.filter(text=q_text).first()

                if options['dry_run']:
                    created += 1
                    continue

                if existing:
                    if not options['update_existing']:
                        skipped += 1
                        continue
                    for k, v in defaults.items():
                        setattr(existing, k, v)
                    obj = existing
                    updated += 1
                else:
                    obj = Question(**defaults)
                    created += 1

                img_rel = (row.get('question_image') or row.get('image') or '').strip()
                if img_rel and images_base:
                    img_path = images_base / img_rel
                    if not img_path.exists():
                        img_path = images_base.parent / img_rel
                    if img_path.exists():
                        with img_path.open('rb') as fh:
                            obj.image.save(img_path.name, File(fh), save=False)

                obj.save()

        run()

        self.stdout.write(self.style.SUCCESS(
            f'Category slug: {category.slug}\n'
            f'Created: {created} | Updated: {updated} | Skipped: {skipped}'
            + (' (dry-run)' if options['dry_run'] else '')
        ))
