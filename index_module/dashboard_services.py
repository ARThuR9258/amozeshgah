import json
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils.encoding import force_str
from django.utils import timezone

from index_module.models import ContactMessage
from quizbuilder_module.models import Quiz, QuizQuestion, UserQuiz, UserQuizQuestionAnswer
from sample_questions.models import SampleQuestion
from subscriptions_module.models import (
    CreditTransaction,
    PaymentOrder,
    SubscriptionPlan,
    UserSubscription,
)

User = get_user_model()


def get_dashboard_stats():
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    paid_orders = PaymentOrder.objects.filter(status=PaymentOrder.Status.PAID)
    sales_today = paid_orders.filter(paid_at__gte=today_start).aggregate(
        total=Sum('amount')
    )['total'] or 0
    sales_week = paid_orders.filter(paid_at__gte=week_start).aggregate(
        total=Sum('amount')
    )['total'] or 0
    sales_month = paid_orders.filter(paid_at__gte=month_start).aggregate(
        total=Sum('amount')
    )['total'] or 0

    return {
        'users_count': User.objects.count(),
        'users_staff_count': User.objects.filter(is_staff=True).count(),
        'quizzes_count': Quiz.objects.count(),
        'quizzes_open_count': Quiz.objects.filter(status='open').count(),
        'sample_questions_count': SampleQuestion.objects.filter(is_active=True).count(),
        'quiz_questions_count': QuizQuestion.objects.count(),
        'user_quizzes_count': UserQuiz.objects.count(),
        'answers_count': UserQuizQuestionAnswer.objects.count(),
        'plans_count': SubscriptionPlan.objects.filter(is_active=True).count(),
        'active_subscriptions_count': UserSubscription.objects.filter(
            is_active=True, status=UserSubscription.Status.ACTIVE
        ).count(),
        'pending_orders_count': PaymentOrder.objects.filter(
            status=PaymentOrder.Status.PENDING
        ).count(),
        'paid_orders_count': paid_orders.count(),
        'sales_today': sales_today,
        'sales_week': sales_week,
        'sales_month': sales_month,
        'unread_messages_count': ContactMessage.objects.filter(is_read=False).count(),
        'messages_count': ContactMessage.objects.count(),
        'credits_transactions_count': CreditTransaction.objects.count(),
    }


def get_sales_chart_bars(stats):
    """درصد نوار نمودار فروش نسبت به بیشترین مقدار."""
    values = {
        'today': stats['sales_today'],
        'week': stats['sales_week'],
        'month': stats['sales_month'],
    }
    peak = max(values.values()) or 1
    return {key: max(4, int((val / peak) * 100)) for key, val in values.items()}


def get_recent_contact_messages(limit=5):
    return ContactMessage.objects.order_by('-created_at')[:limit]


def get_recent_orders(limit=5):
    return PaymentOrder.objects.select_related('user', 'plan').order_by('-created_at')[:limit]


def get_recent_users(limit=5):
    return User.objects.order_by('-date_joined')[:limit]


def _last_n_days_labels(days=14):
    """برچسب‌های N روز اخیر برای محور افقی نمودار."""
    today = timezone.localdate()
    dates = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    labels = []
    for d in dates:
        labels.append(f'{d.day}/{d.month}')
    return dates, labels


def _map_daily_series(dates, queryset, value_key='c'):
    """نگاشت نتیجه TruncDate به آرایه هم‌تراز با روزها."""
    data = {row['d']: row[value_key] or 0 for row in queryset}
    return [int(data.get(d, 0)) for d in dates]


def get_dashboard_charts_data(days=14):
    """داده‌های نمودارهای داشبورد از دیتابیس."""
    date_list, labels = _last_n_days_labels(days)
    range_start = timezone.make_aware(datetime.combine(date_list[0], time.min))

    # ثبت‌نام کاربران روزانه
    users_daily_qs = (
        User.objects.filter(date_joined__gte=range_start)
        .annotate(d=TruncDate('date_joined'))
        .values('d')
        .annotate(c=Count('id'))
        .order_by('d')
    )
    users_daily = _map_daily_series(date_list, users_daily_qs)

    # فروش روزانه (پرداخت‌شده)
    sales_daily_qs = (
        PaymentOrder.objects.filter(
            status=PaymentOrder.Status.PAID,
            paid_at__gte=range_start,
        )
        .annotate(d=TruncDate('paid_at'))
        .values('d')
        .annotate(total=Sum('amount'))
        .order_by('d')
    )
    sales_daily = _map_daily_series(date_list, sales_daily_qs, value_key='total')

    # شرکت در آزمون روزانه
    quizzes_daily_qs = (
        UserQuiz.objects.filter(start_time__gte=range_start)
        .annotate(d=TruncDate('start_time'))
        .values('d')
        .annotate(c=Count('id'))
        .order_by('d')
    )
    quizzes_daily = _map_daily_series(date_list, quizzes_daily_qs)

    # وضعیت سفارش‌ها
    order_status_rows = (
        PaymentOrder.objects.values('status')
        .annotate(c=Count('id'))
        .order_by('-c')
    )
    order_status_labels = []
    order_status_values = []
    order_status_colors = {
        PaymentOrder.Status.PAID: '#10b981',
        PaymentOrder.Status.PENDING: '#f59e0b',
        PaymentOrder.Status.FAILED: '#ef4444',
        PaymentOrder.Status.CANCELLED: '#94a3b8',
    }
    for row in order_status_rows:
        status = row['status']
        order_status_labels.append(
            force_str(dict(PaymentOrder.Status.choices).get(status, status))
        )
        order_status_values.append(row['c'])
    order_status_bg = [order_status_colors.get(row['status'], '#6366f1') for row in order_status_rows]

    # وضعیت اشتراک کاربران
    sub_rows = (
        User.objects.values('subscription_status')
        .annotate(c=Count('id'))
        .order_by('-c')
    )
    sub_labels = []
    sub_values = []
    sub_colors = {
        User.SubscriptionStatus.FREE: '#6366f1',
        User.SubscriptionStatus.CREDIT: '#06b6d4',
        User.SubscriptionStatus.PREMIUM: '#8b5cf6',
        User.SubscriptionStatus.EXPIRED: '#f59e0b',
    }
    for row in sub_rows:
        key = row['subscription_status']
        sub_labels.append(force_str(dict(User.SubscriptionStatus.choices).get(key, key)))
        sub_values.append(row['c'])
    sub_bg = [sub_colors.get(row['subscription_status'], '#94a3b8') for row in sub_rows]

    # وضعیت پاسخنامه آزمون
    from quizbuilder_module.helpers import UserQuizChoice

    quiz_rows = (
        UserQuiz.objects.values('status')
        .annotate(c=Count('id'))
        .order_by('-c')
    )
    quiz_labels = []
    quiz_values = []
    quiz_colors = {
        UserQuizChoice.PENDING: '#f59e0b',
        UserQuizChoice.DONE: '#6366f1',
        UserQuizChoice.PASS: '#10b981',
        UserQuizChoice.FAIL: '#ef4444',
    }
    for row in quiz_rows:
        key = row['status']
        quiz_labels.append(force_str(dict(UserQuizChoice.CHOICES).get(key, key)))
        quiz_values.append(row['c'])
    quiz_bg = [quiz_colors.get(row['status'], '#94a3b8') for row in quiz_rows]

    # پرفروش‌ترین پلن‌ها
    plan_rows = (
        PaymentOrder.objects.filter(status=PaymentOrder.Status.PAID)
        .values('plan__name')
        .annotate(total=Sum('amount'), c=Count('id'))
        .order_by('-total')[:6]
    )
    plan_labels = [row['plan__name'] or '—' for row in plan_rows]
    plan_values = [int(row['total'] or 0) for row in plan_rows]

    # پیام تماس بر اساس موضوع
    msg_rows = (
        ContactMessage.objects.values('subject')
        .annotate(c=Count('id'))
        .order_by('-c')
    )
    msg_labels = []
    msg_values = []
    for row in msg_rows:
        key = row['subject']
        msg_labels.append(force_str(dict(ContactMessage.SUBJECT_CHOICES).get(key, key)))
        msg_values.append(row['c'])

    return {
        'labels': labels,
        'users_daily': users_daily,
        'sales_daily': sales_daily,
        'quizzes_daily': quizzes_daily,
        'orders': {
            'labels': order_status_labels,
            'values': order_status_values,
            'colors': order_status_bg,
        },
        'subscriptions': {
            'labels': sub_labels,
            'values': sub_values,
            'colors': sub_bg,
        },
        'quizzes': {
            'labels': quiz_labels,
            'values': quiz_values,
            'colors': quiz_bg,
        },
        'top_plans': {
            'labels': plan_labels,
            'values': plan_values,
        },
        'messages': {
            'labels': msg_labels,
            'values': msg_values,
        },
        'totals': {
            'users_period': sum(users_daily),
            'sales_period': sum(sales_daily),
            'quizzes_period': sum(quizzes_daily),
        },
    }


def get_dashboard_charts_json(days=14):
    return json.dumps(get_dashboard_charts_data(days), ensure_ascii=False)
