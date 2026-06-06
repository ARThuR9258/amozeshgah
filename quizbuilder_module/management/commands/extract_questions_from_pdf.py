"""
استخراج سوالات از PDF با OCR و ذخیره JSON.

نصب وابستگی‌ها:
  pip install pymupdf easyocr pillow numpy

مثال:
  python manage.py extract_questions_from_pdf ^
    --pdf "C:\\Users\\...\\isargaran82__2.pdf" ^
    --output data/import/isargaran82_questions.json ^
    --images-dir data/import/isargaran82_images
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from quizbuilder_module.pdf_import.ocr_extract import extract_page_images, extract_pdf_text
from quizbuilder_module.pdf_import.parse_questions import merge_short_options, parse_document


class Command(BaseCommand):
    help = 'OCR و استخراج سوالات آیین‌نامه از PDF به فرمت JSON'

    def add_arguments(self, parser):
        parser.add_argument('--pdf', required=True, help='مسیر فایل PDF')
        parser.add_argument(
            '--output',
            default='data/import/questions.json',
            help='مسیر خروجی JSON',
        )
        parser.add_argument(
            '--images-dir',
            default='data/import/question_images',
            help='پوشه ذخیره تصاویر استخراج‌شده',
        )
        parser.add_argument(
            '--skip-pages',
            type=int,
            default=1,
            help='تعداد صفحات ابتدایی که نادیده گرفته شوند (مثلاً جلد)',
        )
        parser.add_argument(
            '--no-ocr',
            action='store_true',
            help='فقط متن داخلی PDF (بدون EasyOCR)',
        )
        parser.add_argument(
            '--ocr-zoom',
            type=float,
            default=2.0,
            help='بزرگنمایی رندر صفحه برای OCR',
        )

    def handle(self, *args, **options):
        pdf_path = Path(options['pdf']).expanduser().resolve()
        if not pdf_path.exists():
            raise CommandError(f'PDF not found: {pdf_path}')

        output_path = Path(options['output'])
        images_dir = Path(options['images_dir'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        reader = None
        if not options['no_ocr']:
            try:
                import easyocr
                self.stdout.write('Loading EasyOCR (fa, en)…')
                reader = easyocr.Reader(['fa', 'en'], gpu=False, verbose=False)
            except ImportError as exc:
                raise CommandError(
                    'easyocr not installed. Run: pip install easyocr pymupdf pillow numpy'
                ) from exc

        import fitz

        doc = fitz.open(pdf_path)
        page_texts: list[str] = []
        page_images: dict[int, list[str]] = {}
        skip = options['skip_pages']

        self.stdout.write(f'Processing {doc.page_count} pages…')
        for i in range(doc.page_count):
            page = doc[i]
            page_num = i + 1
            if i < skip:
                page_texts.append('')
                continue
            self.stdout.write(f'  Page {page_num}/{doc.page_count}…', ending='')
            self.stdout.flush()
            if reader:
                from quizbuilder_module.pdf_import.ocr_extract import extract_page_text

                text = extract_page_text(page, reader=reader, zoom=options['ocr_zoom'])
            else:
                text = page.get_text('text')
            page_texts.append(text)
            imgs = extract_page_images(page, images_dir, page_num)
            if imgs:
                page_images[page_num] = imgs
            self.stdout.write(self.style.SUCCESS(' ok'))

        doc.close()

        raw_path = output_path.with_suffix('.raw.txt')
        raw_path.write_text(
            '\n\n'.join(f'--- PAGE {i + 1} ---\n{t}' for i, t in enumerate(page_texts)),
            encoding='utf-8',
        )
        self.stdout.write(f'Raw text: {raw_path}')

        active_texts = page_texts[skip:] if skip else page_texts
        questions = merge_short_options(
            parse_document(
                active_texts,
                page_images=page_images,
                start_page=skip + 1,
            )
        )
        payload = [q.to_json_dict() for q in questions]

        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

        with_opts = sum(1 for q in payload if q.get('option1'))
        with_ans = sum(1 for q in payload if q.get('correct_answer'))
        with_img = sum(1 for q in payload if q.get('question_image'))

        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(payload)} questions -> {output_path}\n'
            f'  with options: {with_opts}\n'
            f'  with correct_answer: {with_ans}\n'
            f'  with image: {with_img}\n'
            f'Review JSON and fix OCR errors before import.'
        ))
