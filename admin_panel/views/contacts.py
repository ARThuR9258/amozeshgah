from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from admin_panel.htmx import htmx_trigger
from index_module.models import ContactMessage

from .crud_base import ListPageView, paginate


class ContactListView(ListPageView):
    template_name = 'admin_panel/contacts/list.html'
    table_url_name = 'admin_panel:contacts_table'
    create_url_name = ''
    page_title = 'پیام‌های تماس'
    page_subtitle = 'مشاهده و مدیریت پیام‌های کاربران'
    page_icon = 'fa-envelope'
    page_accent = 'ap-accent-amber'
    table_id = 'apContactsTable'
    refresh_event = 'apRefreshContacts'


class ContactTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/contacts/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = ContactMessage.objects.order_by('-created_at')
        if self.request.GET.get('unread') == '1':
            qs = qs.filter(is_read=False)
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(message__icontains=q)
            )
        page_obj, _ = paginate(self.request, qs, 25)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'unread': self.request.GET.get('unread', '')}
        return ctx


class ContactDetailView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/contacts/detail.html'

    def get(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        if not msg.is_read:
            msg.is_read = True
            msg.save(update_fields=['is_read'])
        return super().get(request, pk=pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['msg'] = get_object_or_404(ContactMessage, pk=kwargs['pk'])
        return ctx


class ContactDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(ContactMessage, pk=pk).delete()
        if request.headers.get('HX-Request'):
            return htmx_trigger({'apRefreshContacts': True, 'apToast': 'پیام حذف شد.'})
        return redirect('admin_panel:contacts_list')


class ContactToggleReadView(AdminRequiredMixin, View):
    def post(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        msg.is_read = not msg.is_read
        msg.save(update_fields=['is_read'])
        if request.headers.get('HX-Request'):
            return htmx_trigger({'apRefreshContacts': True, 'apToast': 'وضعیت پیام به‌روز شد.'})
        return redirect('admin_panel:contacts_detail', pk=pk)
