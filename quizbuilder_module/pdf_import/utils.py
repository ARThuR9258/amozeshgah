import re

PERSIAN_DIGIT_MAP = str.maketrans(
    '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬',
    '01234567890123456789.,',
)


def normalize_digits(text: str) -> str:
    if not text:
        return ''
    return text.translate(PERSIAN_DIGIT_MAP)


def clean_text(text: str) -> str:
    text = normalize_digits(text or '')
    text = text.replace('\u200c', ' ').replace('\xa0', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def page_is_readable(pdf_text: str) -> bool:
    """صفحه‌ای که متن واقعی فارسی دارد (نه فونت خراب)."""
    keywords = ('ممنوع', 'خودرو', 'رانندگی', 'سبقت', 'تابلو', 'پیچ')
    return sum(pdf_text.count(k) for k in keywords) >= 3
