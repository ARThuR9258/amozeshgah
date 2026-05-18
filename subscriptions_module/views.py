from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .models import PaymentOrder, SubscriptionPlan
from .services import fulfill_order


class PricingView(TemplateView):
    """صفحه پلن‌ها و مقایسه امکانات."""

    template_name = 'subscriptions_module/pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('display_order')
        credit_plans = plans.filter(plan_type=SubscriptionPlan.PlanType.CREDIT)
        subscription_plans = plans.filter(
            plan_type__in=(
                SubscriptionPlan.PlanType.MONTHLY,
                SubscriptionPlan.PlanType.YEARLY,
            )
        )
        free_plan = plans.filter(plan_type=SubscriptionPlan.PlanType.FREE).first()

        context.update({
            'plans': plans,
            'free_plan': free_plan,
            'credit_plans': credit_plans,
            'subscription_plans': subscription_plans,
            'comparison_features': self._comparison_rows(),
        })

        if self.request.user.is_authenticated:
            from .services import can_take_quiz
            context['user_access'] = can_take_quiz(self.request.user)

        return context

    def _comparison_rows(self):
        return [
            {'name': 'تعداد آزمون', 'free': '۲ در روز', 'credit': 'بر اساس بسته', 'monthly': 'نامحدود', 'yearly': 'نامحدود'},
            {'name': 'پاسخنامه تشریحی', 'free': False, 'credit': True, 'monthly': True, 'yearly': True},
            {'name': 'آمار پیشرفت', 'free': 'محدود', 'credit': True, 'monthly': True, 'yearly': True},
            {'name': 'پشتیبانی اولویت‌دار', 'free': False, 'credit': False, 'monthly': True, 'yearly': True},
            {'name': 'به‌روزرسانی سوالات', 'free': True, 'credit': True, 'monthly': True, 'yearly': True},
            {'name': 'تخفیف نسبت به ماهانه', 'free': '—', 'credit': '—', 'monthly': '—', 'yearly': '۴۰٪ ارزان‌تر'},
        ]


class CheckoutView(LoginRequiredMixin, View):
    """صفحه تسویه حساب — نمایش پلن و آماده اتصال درگاه."""

    template_name = 'subscriptions_module/checkout.html'

    def get(self, request, plan_slug):
        plan = get_object_or_404(
            SubscriptionPlan,
            slug=plan_slug,
            is_active=True,
        )
        if plan.plan_type == SubscriptionPlan.PlanType.FREE:
            messages.info(request, 'پلن رایگان نیاز به پرداخت ندارد.')
            return redirect('subscriptions:pricing')

        return render(request, self.template_name, {
            'plan': plan,
            'final_price': plan.price,
        })

    def post(self, request, plan_slug):
        """ایجاد سفارش — در حالت توسعه پرداخت شبیه‌سازی می‌شود."""
        plan = get_object_or_404(
            SubscriptionPlan,
            slug=plan_slug,
            is_active=True,
        )
        if plan.plan_type == SubscriptionPlan.PlanType.FREE:
            return redirect('subscriptions:pricing')

        with transaction.atomic():
            order = PaymentOrder.objects.create(
                user=request.user,
                plan=plan,
                amount=plan.price,
                status=PaymentOrder.Status.PENDING,
                authority=f'dev-{request.user.id}-{plan.id}',
            )

        # TODO: اتصال زرین‌پال — redirect به درگاه
        # فعلاً شبیه‌سازی پرداخت موفق
        fulfill_order(order)
        messages.success(
            request,
            f'پرداخت با موفقیت انجام شد. پلن «{plan.name}» برای شما فعال شد.',
        )

        next_quiz = request.GET.get('quiz_id') or request.POST.get('quiz_id')
        if next_quiz:
            return redirect('quizbuilder:take_quiz', quiz_id=next_quiz)
        return redirect('subscriptions:pricing')


class PaymentCallbackView(LoginRequiredMixin, View):
    """
    کال‌بک درگاه پرداخت (زرین‌پال و ...).
    Authority و Status از query string خوانده می‌شود.
    """

    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        if not authority:
            messages.error(request, 'اطلاعات پرداخت نامعتبر است.')
            return redirect('subscriptions:pricing')

        order = get_object_or_404(
            PaymentOrder,
            authority=authority,
            user=request.user,
        )

        if status == 'OK':
            fulfill_order(order)
            messages.success(request, 'پرداخت با موفقیت تأیید شد.')
        else:
            order.status = PaymentOrder.Status.FAILED
            order.save(update_fields=['status'])
            messages.error(request, 'پرداخت ناموفق بود.')

        return redirect('subscriptions:pricing')
