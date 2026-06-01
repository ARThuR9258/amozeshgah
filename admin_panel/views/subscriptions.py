from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from subscriptions_module.forms import (
    PaymentOrderDashboardForm,
    SubscriptionPlanDashboardForm,
    UserSubscriptionDashboardForm,
)
from subscriptions_module.models import CreditTransaction, PaymentOrder, SubscriptionPlan, UserSubscription

from .crud_base import ListPageView, ModalFormView, paginate


class PlanListView(ListPageView):
    template_name = 'admin_panel/plans/list.html'
    table_url_name = 'admin_panel:plans_table'
    create_url_name = 'admin_panel:plans_create'
    page_title = 'پلن‌ها'
    page_subtitle = 'مدیریت پلن‌های اشتراک'
    page_icon = 'fa-gem'
    page_accent = 'ap-accent-violet'
    table_id = 'apPlansTable'
    refresh_event = 'apRefreshPlans'


class PlanTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/plans/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = SubscriptionPlan.objects.order_by('display_order', 'price')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
        page_obj, _ = paginate(self.request, qs, 20)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q}
        return ctx


class PlanCreateView(ModalFormView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanDashboardForm
    create_title = 'پلن جدید'
    form_icon = 'fa-gem'
    form_subtitle = 'تعریف پلن اشتراک، قیمت و امکانات'
    section_icon = 'fa-gem'
    form_extra_class = 'ap-glass-form--wide'
    refresh_event = 'apRefreshPlans'

    def get(self, request):
        return self._render(request, self.form_class(), self.create_title, self.submit_create)

    def post(self, request):
        form = self.form_class(**self.get_form_kwargs(request))
        if form.is_valid():
            form.save()
            return self._success('پلن ذخیره شد.')
        return self._render(request, form, self.create_title, self.submit_create)


class PlanUpdateView(ModalFormView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanDashboardForm
    form_icon = 'fa-gem'
    form_subtitle = 'ویرایش مشخصات و قیمت پلن'
    section_icon = 'fa-gem'
    form_extra_class = 'ap-glass-form--wide'
    refresh_event = 'apRefreshPlans'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'ویرایش {obj.name}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('پلن به‌روزرسانی شد.')
        return self._render(request, form, f'ویرایش {obj.name}', self.submit_update)


class PlanDeleteView(ModalFormView):
    model = SubscriptionPlan
    refresh_event = 'apRefreshPlans'

    def post(self, request, pk):
        self.get_object(pk).delete()
        return self._success('پلن حذف شد.')


class OrderListView(ListPageView):
    template_name = 'admin_panel/orders/list.html'
    table_url_name = 'admin_panel:orders_table'
    create_url_name = ''
    page_title = 'سفارش‌ها'
    page_subtitle = 'مدیریت سفارش‌های پرداخت'
    page_icon = 'fa-shopping-bag'
    page_accent = 'ap-accent-emerald'
    table_id = 'apOrdersTable'
    refresh_event = 'apRefreshOrders'


class OrderTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/orders/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        status = (self.request.GET.get('status') or '').strip()
        qs = PaymentOrder.objects.select_related('user', 'plan').order_by('-created_at')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__phone_number__icontains=q)
                | Q(plan__name__icontains=q)
            )
        page_obj, _ = paginate(self.request, qs, 25)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'status': status}
        ctx['status_choices'] = PaymentOrder.Status.choices
        return ctx


class OrderUpdateView(ModalFormView):
    model = PaymentOrder
    form_class = PaymentOrderDashboardForm
    refresh_event = 'apRefreshOrders'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'سفارش #{obj.id}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('سفارش به‌روزرسانی شد.')
        return self._render(request, form, f'سفارش #{obj.id}', self.submit_update)


class SubscriptionListView(ListPageView):
    template_name = 'admin_panel/subscriptions/list.html'
    table_url_name = 'admin_panel:subscriptions_table'
    create_url_name = ''
    page_title = 'اشتراک کاربران'
    page_subtitle = 'مدیریت اشتراک‌های فعال و منقضی'
    page_icon = 'fa-id-card'
    page_accent = 'ap-accent-indigo'
    table_id = 'apSubscriptionsTable'
    refresh_event = 'apRefreshSubscriptions'


class SubscriptionTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/subscriptions/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = UserSubscription.objects.select_related('user', 'plan').order_by('-created_at')
        if q:
            qs = qs.filter(Q(user__phone_number__icontains=q) | Q(plan__name__icontains=q))
        page_obj, _ = paginate(self.request, qs, 25)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q}
        return ctx


class SubscriptionUpdateView(ModalFormView):
    model = UserSubscription
    form_class = UserSubscriptionDashboardForm
    form_icon = 'fa-id-card'
    form_subtitle = 'ویرایش اشتراک، تاریخ شروع و انقضا'
    section_icon = 'fa-id-card'
    refresh_event = 'apRefreshSubscriptions'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'اشتراک #{obj.id}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('اشتراک به‌روزرسانی شد.')
        return self._render(request, form, f'اشتراک #{obj.id}', self.submit_update)


class CreditListView(ListPageView):
    template_name = 'admin_panel/credits/list.html'
    table_url_name = 'admin_panel:credits_table'
    create_url_name = ''
    page_title = 'تراکنش اعتبار'
    page_subtitle = 'لیست تراکنش‌های اعتبار کاربران'
    page_icon = 'fa-coins'
    page_accent = 'ap-accent-amber'
    table_id = 'apCreditsTable'
    refresh_event = 'apRefreshCredits'


class CreditTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/credits/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = CreditTransaction.objects.select_related('user').order_by('-created_at')
        if q:
            qs = qs.filter(
                Q(user__phone_number__icontains=q) | Q(description__icontains=q)
            )
        page_obj, _ = paginate(self.request, qs, 30)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q}
        return ctx
