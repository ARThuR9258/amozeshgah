from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from account_module.decorators import AdminRequiredMixin
from amozeshga.dashboard_list import build_pagination_query
from amozeshga.dashboard_form_mixins import dashboard_form_context, form_has_files
from .forms import (
    PaymentOrderDashboardForm,
    SubscriptionPlanDashboardForm,
    UserSubscriptionDashboardForm,
)
from .models import CreditTransaction, PaymentOrder, SubscriptionPlan, UserSubscription
from .services import fulfill_order


class PlanListDashboard(AdminRequiredMixin, ListView):
    model = SubscriptionPlan
    template_name = 'subscriptions_module/dashboard/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20

    def get_queryset(self):
        qs = SubscriptionPlan.objects.all().order_by('display_order', 'price')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
        active = self.request.GET.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['active_filter'] = self.request.GET.get('active', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {
            'total': SubscriptionPlan.objects.count(),
            'active': SubscriptionPlan.objects.filter(is_active=True).count(),
        }
        return context


class _SubFormMixin(AdminRequiredMixin):
    template_name = 'layout/dashboard/model_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form') or self.get_form()
        context.update(self._page_context())
        context['form_enctype'] = (
            'multipart/form-data' if form_has_files(form) else 'application/x-www-form-urlencoded'
        )
        return context

    def _page_context(self):
        raise NotImplementedError


class PlanCreateDashboard(AdminRequiredMixin, CreateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanDashboardForm
    template_name = 'subscriptions_module/dashboard/plan_form.html'
    success_url = reverse_lazy('dashboard_plans')

    def form_valid(self, form):
        messages.success(self.request, 'پلن با موفقیت ایجاد شد.')
        return super().form_valid(form)


class PlanUpdateDashboard(AdminRequiredMixin, UpdateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanDashboardForm
    template_name = 'subscriptions_module/dashboard/plan_form.html'
    success_url = reverse_lazy('dashboard_plans')

    def form_valid(self, form):
        messages.success(self.request, 'پلن با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


class OrderListDashboard(AdminRequiredMixin, ListView):
    model = PaymentOrder
    template_name = 'subscriptions_module/dashboard/order_list.html'
    context_object_name = 'orders'
    paginate_by = 25

    def get_queryset(self):
        qs = PaymentOrder.objects.select_related('user', 'plan').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__phone_number__icontains=q)
                | Q(plan__name__icontains=q)
            )
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {
            'total': PaymentOrder.objects.count(),
            'pending': PaymentOrder.objects.filter(status=PaymentOrder.Status.PENDING).count(),
            'paid': PaymentOrder.objects.filter(status=PaymentOrder.Status.PAID).count(),
        }
        return context


class SubscriptionListDashboard(AdminRequiredMixin, ListView):
    model = UserSubscription
    template_name = 'subscriptions_module/dashboard/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 25

    def get_queryset(self):
        qs = UserSubscription.objects.select_related('user', 'plan').order_by('-started_at')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__phone_number__icontains=q)
                | Q(plan__name__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['status_choices'] = UserSubscription.Status.choices
        context['stats'] = {
            'total': UserSubscription.objects.count(),
            'active': UserSubscription.objects.filter(
                is_active=True, status=UserSubscription.Status.ACTIVE
            ).count(),
        }
        return context


class CreditTransactionListDashboard(AdminRequiredMixin, ListView):
    model = CreditTransaction
    template_name = 'subscriptions_module/dashboard/credit_list.html'
    context_object_name = 'transactions'
    paginate_by = 30

    def get_queryset(self):
        qs = CreditTransaction.objects.select_related('user', 'plan').order_by('-created_at')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__phone_number__icontains=q)
                | Q(description__icontains=q)
            )
        tx_type = self.request.GET.get('type')
        if tx_type:
            qs = qs.filter(transaction_type=tx_type)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['type_choices'] = CreditTransaction.TransactionType.choices
        context['stats'] = {
            'total': CreditTransaction.objects.count(),
            'added': CreditTransaction.objects.filter(amount__gt=0).count(),
        }
        return context


class OrderUpdateDashboard(_SubFormMixin, UpdateView):
    model = PaymentOrder
    form_class = PaymentOrderDashboardForm
    success_url = reverse_lazy('dashboard_orders')

    def get_queryset(self):
        return PaymentOrder.objects.select_related('user', 'plan')

    def _page_context(self):
        o = self.object
        info = (
            f'<p class="mb-1"><strong>کاربر:</strong> {o.user.get_full_name() or o.user.username} '
            f'<small dir="ltr">({o.user.phone_number or "—"})</small></p>'
            f'<p class="mb-0"><strong>پلن:</strong> {o.plan.name} — '
            f'<strong>تاریخ ثبت:</strong> {o.created_at.strftime("%Y/%m/%d %H:%M")}</p>'
        )
        return dashboard_form_context(
            page_title=f'سفارش #{o.pk}',
            page_heading=f'ویرایش سفارش #{o.pk}',
            page_icon='shopping-cart',
            page_subtitle='تغییر وضعیت و اطلاعات پرداخت',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('dashboard_orders'), 'label': 'سفارش‌ها'},
                {'url': None, 'label': f'#{o.pk}'},
            ],
            cancel_url=reverse('dashboard_orders'),
            submit_label='ذخیره سفارش',
            form_section_title='وضعیت و پرداخت',
            form_readonly_info=info,
        )

    def form_valid(self, form):
        old_status = PaymentOrder.objects.filter(pk=self.object.pk).values_list('status', flat=True).first()
        new_status = form.cleaned_data.get('status')
        if new_status == PaymentOrder.Status.PAID and old_status != PaymentOrder.Status.PAID:
            order = form.save(commit=False)
            order.status = PaymentOrder.Status.PENDING
            order.paid_at = None
            order.save()
            fulfill_order(order)
            messages.success(
                self.request,
                'سفارش پرداخت‌شده ثبت شد و مزایا برای کاربر فعال شد.',
            )
            return redirect(self.get_success_url())
        messages.success(self.request, 'سفارش به‌روزرسانی شد.')
        return super().form_valid(form)


class SubscriptionUpdateDashboard(_SubFormMixin, UpdateView):
    model = UserSubscription
    form_class = UserSubscriptionDashboardForm
    success_url = reverse_lazy('dashboard_subscriptions')

    def get_queryset(self):
        return UserSubscription.objects.select_related('user', 'plan')

    def _page_context(self):
        s = self.object
        return dashboard_form_context(
            page_title=f'اشتراک #{s.pk}',
            page_heading=f'ویرایش اشتراک — {s.user.get_full_name() or s.user.username}',
            page_icon='id-card',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('dashboard_subscriptions'), 'label': 'اشتراک‌ها'},
                {'url': None, 'label': 'ویرایش'},
            ],
            cancel_url=reverse('dashboard_subscriptions'),
            form_section_title='مدیریت اشتراک',
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.user.refresh_subscription_status()
        messages.success(self.request, 'اشتراک به‌روزرسانی شد.')
        return response
