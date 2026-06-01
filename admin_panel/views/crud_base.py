from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from admin_panel.htmx import htmx_trigger, render_modal_form


class ModalFormView(AdminRequiredMixin, View):
    form_class = None
    form_template = 'admin_panel/partials/_glass_form.html'
    create_title = ''
    update_title = ''
    submit_create = 'ذخیره'
    submit_update = 'ثبت تغییرات'
    refresh_event = 'apRefreshTable'
    multipart = False
    form_icon = 'fa-plus-circle'
    form_subtitle = ''
    section_title = 'اطلاعات'
    section_icon = 'fa-edit'
    form_extra_class = ''

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get_form_kwargs(self, request, instance=None):
        kwargs = {}
        if request.method in ('POST', 'PUT'):
            kwargs['data'] = request.POST
            if self.multipart:
                kwargs['files'] = request.FILES
        if instance is not None:
            kwargs['instance'] = instance
        return kwargs

    def _render(self, request, form, title, submit_label):
        return render_modal_form(request, self.form_template, {
            'form': form,
            'title': title,
            'submit_label': submit_label,
            'multipart': self.multipart,
            'form_icon': self.form_icon,
            'form_subtitle': self.form_subtitle,
            'section_title': self.section_title,
            'section_icon': self.section_icon,
            'form_extra_class': self.form_extra_class,
        })

    def _success(self, message):
        return htmx_trigger({
            'apModalClose': True,
            self.refresh_event: True,
            'apToast': message,
        })


class ListPageView(AdminRequiredMixin, TemplateView):
    list_template = 'admin_panel/partials/_list_page.html'
    table_url_name = ''
    create_url_name = ''
    page_title = ''
    page_subtitle = ''
    page_icon = 'fa-table'
    page_accent = 'ap-accent-indigo'

    def get_context_data(self, **kwargs):
        from django.urls import reverse
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title
        ctx['page_subtitle'] = self.page_subtitle
        ctx['page_icon'] = self.page_icon
        ctx['page_accent'] = self.page_accent
        ctx['table_url'] = reverse(self.table_url_name)
        if self.create_url_name:
            ctx['create_url'] = reverse(self.create_url_name)
        ctx['table_id'] = getattr(self, 'table_id', 'apDataTable')
        ctx['refresh_event'] = getattr(self, 'refresh_event', 'apRefreshTable')
        return ctx


def paginate(request, queryset, per_page=20):
    page_num = int(request.GET.get('page') or 1)
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_num), paginator
