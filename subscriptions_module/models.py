from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(models.Model):
    """تعریف پلن‌های اشتراک و بسته اعتباری."""

    class PlanType(models.TextChoices):
        FREE = 'free', _('رایگان')
        CREDIT = 'credit', _('بسته اعتباری')
        MONTHLY = 'monthly', _('ماهانه')
        YEARLY = 'yearly', _('سالانه')

    slug = models.SlugField(unique=True, verbose_name='شناسه یکتا')
    name = models.CharField(max_length=120, verbose_name='نام پلن')
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices,
        verbose_name='نوع پلن',
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    price = models.PositiveIntegerField(
        default=0,
        verbose_name='قیمت (تومان)',
        help_text='برای پلن رایگان صفر باشد.',
    )
    credits_amount = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد اعتبار',
        help_text='فقط برای بسته‌های اعتباری.',
    )
    duration_days = models.PositiveIntegerField(
        default=0,
        verbose_name='مدت اشتراک (روز)',
        help_text='برای پلن ماهانه/سالانه.',
    )
    daily_free_attempts = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='آزمون رایگان روزانه',
        help_text='فقط برای پلن رایگان.',
    )
    features = models.JSONField(
        default=list,
        blank=True,
        verbose_name='لیست امکانات',
    )
    is_popular = models.BooleanField(default=False, verbose_name='پلن محبوب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پلن اشتراک'
        verbose_name_plural = 'پلن‌های اشتراک'
        ordering = ['display_order', 'price']

    def __str__(self):
        return self.name

    @property
    def is_unlimited(self):
        """اشتراک با دسترسی نامحدود به آزمون."""
        return self.plan_type in (
            self.PlanType.MONTHLY,
            self.PlanType.YEARLY,
        )


class UserSubscription(models.Model):
    """اشتراک فعال یا تاریخچه اشتراک کاربر."""

    class Status(models.TextChoices):
        ACTIVE = 'active', _('فعال')
        EXPIRED = 'expired', _('منقضی')
        CANCELLED = 'cancelled', _('لغو شده')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='کاربر',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='user_subscriptions',
        verbose_name='پلن',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='وضعیت',
    )
    started_at = models.DateTimeField(default=timezone.now, verbose_name='شروع')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='پایان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'اشتراک کاربر'
        verbose_name_plural = 'اشتراک‌های کاربران'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} — {self.plan.name}'

    @property
    def is_valid(self):
        if not self.is_active or self.status != self.Status.ACTIVE:
            return False
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        return self.plan.is_unlimited


class CreditTransaction(models.Model):
    """تاریخچه خرید و مصرف اعتبار."""

    class TransactionType(models.TextChoices):
        PURCHASE = 'purchase', _('خرید اعتبار')
        CONSUME = 'consume', _('مصرف در آزمون')
        REFUND = 'refund', _('بازگشت')
        BONUS = 'bonus', _('هدیه')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_transactions',
        verbose_name='کاربر',
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name='نوع تراکنش',
    )
    amount = models.IntegerField(
        verbose_name='مقدار',
        help_text='مثبت برای افزایش، منفی برای کاهش اعتبار.',
    )
    balance_after = models.PositiveIntegerField(verbose_name='موجودی پس از تراکنش')
    description = models.CharField(max_length=255, blank=True, verbose_name='توضیح')
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions',
        verbose_name='پلن مرتبط',
    )
    order = models.ForeignKey(
        'PaymentOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions',
        verbose_name='سفارش',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تراکنش اعتبار'
        verbose_name_plural = 'تراکنش‌های اعتبار'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} | {self.get_transaction_type_display()} | {self.amount}'


class PaymentOrder(models.Model):
    """سفارش پرداخت — آماده اتصال به درگاه."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('در انتظار پرداخت')
        PAID = 'paid', _('پرداخت شده')
        FAILED = 'failed', _('ناموفق')
        CANCELLED = 'cancelled', _('لغو شده')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_orders',
        verbose_name='کاربر',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='پلن',
    )
    amount = models.PositiveIntegerField(verbose_name='مبلغ (تومان)')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='وضعیت',
    )
    authority = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='کد مرجع درگاه',
        help_text='Authority زرین‌پال یا مشابه.',
    )
    ref_id = models.CharField(max_length=64, blank=True, verbose_name='شماره پیگیری')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'سفارش پرداخت'
        verbose_name_plural = 'سفارش‌های پرداخت'
        ordering = ['-created_at']

    def __str__(self):
        return f'سفارش #{self.pk} — {self.user} — {self.plan.name}'
