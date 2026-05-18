"""
منطق دسترسی به آزمون و مدیریت اعتبار/اشتراک.
"""
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import CreditTransaction, SubscriptionPlan, UserSubscription


# حداکثر آزمون رایگان روزانه برای کاربران بدون اشتراک/اعتبار
MAX_DAILY_FREE_ATTEMPTS = 2


@dataclass
class QuizAccessResult:
    """نتیجه بررسی دسترسی به آزمون."""

    allowed: bool
    reason: str = ''
    access_type: str = ''  # unlimited | credit | free_daily | denied
    credits_remaining: int = 0
    free_attempts_remaining: int = 0
    message: str = ''

    @property
    def should_redirect_pricing(self):
        return not self.allowed and self.access_type == 'denied'


def get_active_subscription(user):
    """اشتراک نامحدود فعال کاربر."""
    now = timezone.now()
    return (
        UserSubscription.objects.filter(
            user=user,
            is_active=True,
            status=UserSubscription.Status.ACTIVE,
            plan__plan_type__in=(
                SubscriptionPlan.PlanType.MONTHLY,
                SubscriptionPlan.PlanType.YEARLY,
            ),
        )
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        .select_related('plan')
        .order_by('-expires_at')
        .first()
    )


def _reset_daily_free_attempts(user):
    """ریست شمارنده آزمون رایگان در ابتدای روز جدید."""
    today = timezone.now().date()
    if user.last_attempt_date != today:
        user.exam_attempts = 0
        user.last_attempt_date = today
        user.save(update_fields=['exam_attempts', 'last_attempt_date'])


def can_take_quiz(user) -> QuizAccessResult:
    """
    بررسی امکان شرکت در آزمون:
    - اشتراک فعال → نامحدود
    - اعتبار > 0 → مجاز (کسر هنگام شروع)
    - سهمیه رایگان روزانه → مجاز
    - غیر این صورت → رد
    """
    if user.is_staff or user.is_superuser:
        return QuizAccessResult(
            allowed=True,
            access_type='unlimited',
            message='دسترسی مدیر',
        )

    user.refresh_subscription_status()

    # اشتراک نامحدود فعال
    sub = get_active_subscription(user)
    if sub:
        return QuizAccessResult(
            allowed=True,
            access_type='unlimited',
            message=f'اشتراک {sub.plan.name} فعال است.',
        )

    credits = user.credits or 0
    if credits > 0:
        return QuizAccessResult(
            allowed=True,
            access_type='credit',
            credits_remaining=credits,
            message=f'{credits} اعتبار باقی‌مانده',
        )

    _reset_daily_free_attempts(user)
    free_left = max(0, MAX_DAILY_FREE_ATTEMPTS - user.exam_attempts)
    if free_left > 0:
        return QuizAccessResult(
            allowed=True,
            access_type='free_daily',
            free_attempts_remaining=free_left,
            message=f'{free_left} آزمون رایگان امروز',
        )

    return QuizAccessResult(
        allowed=False,
        access_type='denied',
        reason='no_access',
        message='اعتبار یا اشتراک فعال ندارید. لطفاً یک پلن انتخاب کنید.',
    )


@transaction.atomic
def consume_quiz_access(user, access_type: str) -> None:
    """پس از شروع آزمون، سهمیه یا اعتبار را کسر کن."""
    if access_type == 'unlimited':
        return

    if access_type == 'credit':
        user.credits = max(0, (user.credits or 0) - 1)
        balance = user.credits
        user.save(update_fields=['credits'])
        if user.credits == 0 and not user.is_premium:
            user.subscription_status = user.SubscriptionStatus.FREE
            user.save(update_fields=['subscription_status'])
        CreditTransaction.objects.create(
            user=user,
            transaction_type=CreditTransaction.TransactionType.CONSUME,
            amount=-1,
            balance_after=balance,
            description='مصرف اعتبار برای شرکت در آزمون',
        )
        return

    if access_type == 'free_daily':
        _reset_daily_free_attempts(user)
        user.exam_attempts += 1
        user.last_attempt_date = timezone.now().date()
        user.save(update_fields=['exam_attempts', 'last_attempt_date'])


@transaction.atomic
def fulfill_order(order):
    """فعال‌سازی پلن پس از پرداخت موفق."""
    from .models import PaymentOrder

    if order.status == PaymentOrder.Status.PAID:
        return

    user = order.user
    plan = order.plan
    order.status = PaymentOrder.Status.PAID
    order.paid_at = timezone.now()
    order.save(update_fields=['status', 'paid_at'])

    if plan.plan_type == SubscriptionPlan.PlanType.CREDIT:
        user.credits = (user.credits or 0) + plan.credits_amount
        user.subscription_status = user.SubscriptionStatus.CREDIT
        user.save(update_fields=['credits', 'subscription_status'])
        CreditTransaction.objects.create(
            user=user,
            transaction_type=CreditTransaction.TransactionType.PURCHASE,
            amount=plan.credits_amount,
            balance_after=user.credits,
            description=f'خرید بسته {plan.name}',
            plan=plan,
            order=order,
        )
    elif plan.is_unlimited:
        expires = timezone.now() + timedelta(days=plan.duration_days or 30)
        # غیرفعال کردن اشتراک‌های قبلی
        UserSubscription.objects.filter(user=user, is_active=True).update(
            is_active=False,
            status=UserSubscription.Status.EXPIRED,
        )
        UserSubscription.objects.create(
            user=user,
            plan=plan,
            status=UserSubscription.Status.ACTIVE,
            is_active=True,
            expires_at=expires,
        )
        user.is_premium = True
        user.subscription_status = user.SubscriptionStatus.PREMIUM
        user.save(update_fields=['is_premium', 'subscription_status'])
