from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic import TemplateView

from account_module.forms import UserAddDashboardForm, UserEditDashboardForm
from admin_panel.auth import AdminRequiredMixin
from admin_panel.htmx import htmx_trigger

from .crud_base import ListPageView, ModalFormView, paginate

User = get_user_model()


class UserListView(ListPageView):
    template_name = 'admin_panel/users/list.html'
    table_url_name = 'admin_panel:users_table'
    create_url_name = 'admin_panel:users_create'
    page_title = 'مدیریت کاربران'
    page_subtitle = 'لیست، افزودن، ویرایش و حذف کاربران'
    page_icon = 'fa-users'
    page_accent = 'ap-accent-indigo'
    table_id = 'apUsersTable'
    refresh_event = 'apRefreshUsers'


class UserTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/users/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = User.objects.order_by('-date_joined')
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(phone_number__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        role = self.request.GET.get('role')
        if role == 'staff':
            qs = qs.filter(is_staff=True)
        active = self.request.GET.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)

        page_obj, _ = paginate(self.request, qs, 20)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'role': role or '', 'active': active or ''}
        return ctx


class UserCreateView(ModalFormView):
    model = User
    form_class = UserAddDashboardForm
    form_template = 'admin_panel/users/_form.html'
    create_title = 'کاربر جدید'
    refresh_event = 'apRefreshUsers'
    list_url_name = 'admin_panel:users_list'

    def get(self, request):
        return self._render(request, self.form_class(), self.create_title, self.submit_create)

    def post(self, request):
        form = self.form_class(**self.get_form_kwargs(request))
        if form.is_valid():
            form.save()
            return self._success('کاربر ایجاد شد.')
        return self._render(request, form, self.create_title, self.submit_create)


class UserUpdateView(ModalFormView):
    model = User
    form_class = UserEditDashboardForm
    form_template = 'admin_panel/users/_form.html'
    refresh_event = 'apRefreshUsers'
    list_url_name = 'admin_panel:users_list'

    def get(self, request, pk):
        obj = self.get_object(pk)
        label = obj.get_full_name() or obj.username or obj.phone_number
        return self._render(request, self.form_class(instance=obj), f'ویرایش {label}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        label = obj.get_full_name() or obj.username or obj.phone_number
        if form.is_valid():
            form.save()
            return self._success('کاربر به‌روزرسانی شد.')
        return self._render(request, form, f'ویرایش {label}', self.submit_update)


class UserDeleteView(ModalFormView):
    model = User
    refresh_event = 'apRefreshUsers'
    list_url_name = 'admin_panel:users_list'

    def post(self, request, pk):
        obj = self.get_object(pk)
        if obj == request.user:
            return htmx_trigger({'apToast': 'نمی‌توانید خودتان را حذف کنید.'})
        obj.delete()
        return self._success('کاربر حذف شد.')
