from django.core.management.base import BaseCommand

from subscriptions_module.models import SubscriptionPlan


PLANS = [
    {
        'slug': 'free',
        'name': 'رایگان',
        'plan_type': SubscriptionPlan.PlanType.FREE,
        'price': 0,
        'credits_amount': 0,
        'duration_days': 0,
        'daily_free_attempts': 2,
        'display_order': 0,
        'features': [
            '۲ آزمون رایگان در روز',
            'دسترسی به سوالات پایه',
            'نمایش نمره',
        ],
    },
    {
        'slug': 'credit-10',
        'name': 'بسته ۱۰ اعتبار',
        'plan_type': SubscriptionPlan.PlanType.CREDIT,
        'price': 49_000,
        'credits_amount': 10,
        'display_order': 1,
        'features': [
            '۱۰ آزمون کامل',
            'پاسخنامه تشریحی',
            'بدون محدودیت زمانی',
        ],
    },
    {
        'slug': 'credit-25',
        'name': 'بسته ۲۵ اعتبار',
        'plan_type': SubscriptionPlan.PlanType.CREDIT,
        'price': 99_000,
        'credits_amount': 25,
        'display_order': 2,
        'features': [
            '۲۵ آزمون کامل',
            'پاسخنامه تشریحی',
            'صرفه‌جویی ۲۰٪',
        ],
    },
    {
        'slug': 'credit-50',
        'name': 'بسته ۵۰ اعتبار',
        'plan_type': SubscriptionPlan.PlanType.CREDIT,
        'price': 169_000,
        'credits_amount': 50,
        'display_order': 3,
        'features': [
            '۵۰ آزمون کامل',
            'پاسخنامه تشریحی',
            'بهترین قیمت بسته اعتباری',
        ],
    },
    {
        'slug': 'monthly',
        'name': 'اشتراک ماهانه',
        'plan_type': SubscriptionPlan.PlanType.MONTHLY,
        'price': 199_000,
        'duration_days': 30,
        'display_order': 4,
        'is_popular': True,
        'features': [
            'آزمون نامحدود ۳۰ روز',
            'پاسخنامه کامل',
            'آمار پیشرفت',
            'پشتیبانی اولویت‌دار',
        ],
    },
    {
        'slug': 'yearly',
        'name': 'اشتراک سالانه',
        'plan_type': SubscriptionPlan.PlanType.YEARLY,
        'price': 1_490_000,
        'duration_days': 365,
        'display_order': 5,
        'features': [
            'آزمون نامحدود یک سال',
            '۴۰٪ ارزان‌تر از ماهانه',
            'همه امکانات پرمیوم',
            'به‌روزرسانی رایگان',
        ],
    },
]


class Command(BaseCommand):
    help = 'ایجاد یا به‌روزرسانی پلن‌های پیش‌فرض اشتراک'

    def handle(self, *args, **options):
        for item in PLANS:
            data = item.copy()
            slug = data.pop('slug')
            SubscriptionPlan.objects.update_or_create(slug=slug, defaults=data)
        self.stdout.write(self.style.SUCCESS(f'Done: {len(PLANS)} plans created/updated.'))
