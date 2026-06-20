"""تنظیمات مرکزی SEO — Production Ready."""

from django.conf import settings

SITE_NAME = 'آیین‌یار'
SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'ayinyar.ir')
SITE_URL = getattr(settings, 'SITE_URL', f'https://{SITE_DOMAIN}')

DEFAULT_TITLE = 'آیین‌یار | آزمون آنلاین آیین‌نامه رانندگی'
DEFAULT_DESCRIPTION = (
    'آیین‌یار — پلتفرم آزمون آنلاین آیین‌نامه رانندگی با نمونه سوالات به‌روز، '
    'آزمون شبیه‌سازی‌شده و پاسخنامه فوری. موفقیت در آزمون آیین‌نامه را تضمین کنید.'
)
DEFAULT_KEYWORDS = (
    'آزمون آیین نامه, نمونه سوال آیین نامه, آزمون آنلاین آیین نامه, '
    'سوالات آیین نامه رانندگی, قبولی آزمون آیین نامه, آزمون آزمایشی آیین نامه, '
    'تابلوهای راهنمایی رانندگی, سوالات فنی آیین نامه, آیین‌یار'
)

THEME_COLOR = '#4dabf7'
OG_LOCALE = 'fa_IR'
OG_IMAGE = f'{SITE_URL}/static/images/og-default.png'

GOOGLE_SITE_VERIFICATION = getattr(settings, 'GOOGLE_SITE_VERIFICATION', '')
GOOGLE_ANALYTICS_ID = getattr(settings, 'GOOGLE_ANALYTICS_ID', '')

# مسیرهایی که نباید ایندکس شوند
NOINDEX_PREFIXES = (
    '/account/panel/',
    '/account/forgot-password/',
    '/account/reset-password/',
    '/quiz/session/',
    '/quiz/start/',
    '/my-wrong-questions/',
    '/pricing/checkout/',
    '/pricing/payment/',
    '/dashboard/',
    '/admin/',
)

NOINDEX_EXACT = {
    '/account/sign-in/',
    '/account/sign-up/',
    '/account/log-out/',
}

# متای پیش‌فرض صفحات عمومی
PAGE_META = {
    'first_page': {
        'title': 'آیین‌یار | آزمون آنلاین آیین‌نامه رانندگی — نمونه سوالات به‌روز',
        'description': (
            'آزمون آنلاین آیین‌نامه رانندگی با سوالات به‌روز ۱۴۰۴، '
            'نمونه سوال رایگان، آزمون شبیه‌سازی‌شده و پاسخنامه فوری. همین الان شروع کنید.'
        ),
        'keywords': DEFAULT_KEYWORDS,
    },
    'about_page': {
        'title': 'درباره آیین‌یار | پلتفرم آزمون آیین‌نامه رانندگی',
        'description': 'آیین‌یار پلتفرم تخصصی آزمون آنلاین آیین‌نامه رانندگی با هدف کمک به قبولی داوطلبان در آزمون رسمی.',
        'keywords': 'درباره آیین‌یار, آزمون آیین نامه, پلتفرم آموزشی رانندگی',
    },
    'contact_page': {
        'title': 'تماس با آیین‌یار | پشتیبانی آزمون آیین‌نامه',
        'description': 'با تیم پشتیبانی آیین‌یار تماس بگیرید. پاسخگویی سریع به سوالات فنی، اشتراک و آزمون آنلاین.',
        'keywords': 'تماس آیین‌یار, پشتیبانی آزمون آیین نامه',
    },
    # نمونه سوالات — موقتاً غیرفعال
    # 'sample_questions:question_list': {
    #     'title': 'نمونه سوالات آیین نامه رانندگی | دانلود PDF — آیین‌یار',
    #     'description': 'دانلود نمونه سوالات آیین نامه رانندگی به‌روز ۱۴۰۴. مجموعه سوالات تستی با پاسخنامه برای آمادگی آزمون.',
    #     'keywords': 'نمونه سوال آیین نامه, سوالات آیین نامه رانندگی, دانلود سوال آیین نامه',
    # },
    'quizbuilder:exam_hub': {
        'title': 'آزمون آنلاین آیین نامه رانندگی | آیین‌یار',
        'description': 'آزمون آنلاین آیین نامه رانندگی با سوالات به‌روز و شبیه‌ساز واقعی آزمون. ۲۰ سوال، ۳۰ دقیقه، پاسخنامه فوری.',
        'keywords': 'آزمون آنلاین آیین نامه, آزمون آزمایشی آیین نامه, قبولی آزمون آیین نامه',
    },
    'subscriptions:pricing': {
        'title': 'پلن‌ها و قیمت آزمون آیین‌نامه | آیین‌یار',
        'description': 'مشاهده پلن‌های اشتراک آیین‌یار برای آزمون نامحدود آیین‌نامه، نمونه سوالات و تمرین هوشمند.',
        'keywords': 'قیمت آزمون آیین نامه, اشتراک آیین‌یار, پلن آزمون آنلاین',
    },
    'blog:article_list': {
        'title': 'مقالات آموزشی آیین‌نامه رانندگی | آیین‌یار',
        'description': 'مقالات آموزشی، نکات آزمون و راهنمای قبولی در آزمون آیین‌نامه رانندگی.',
        'keywords': 'مقالات آیین نامه, نکات آزمون آیین نامه, آموزش رانندگی',
    },
}
