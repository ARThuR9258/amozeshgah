from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from account_module.decorators import AdminRequiredMixin
from .models import ContactMessage


class ContactMessageListDashboard(AdminRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'index_module/dashboard/contact_list.html'
    context_object_name = 'messages_list'
    paginate_by = 25

    def get_queryset(self):
        qs = ContactMessage.objects.order_by('-created_at')
        if self.request.GET.get('unread') == '1':
            qs = qs.filter(is_read=False)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(email__icontains=q) | Q(message__icontains=q)
            )
        subject = self.request.GET.get('subject')
        if subject:
            qs = qs.filter(subject=subject)
        return qs

    def get_context_data(self, **kwargs):
        from amozeshga.dashboard_list import build_pagination_query

        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['filter_unread'] = self.request.GET.get('unread') == '1'
        context['subject_filter'] = self.request.GET.get('subject', '')
        context['pagination_query'] = build_pagination_query(self.request)
        context['subject_choices'] = ContactMessage.SUBJECT_CHOICES
        context['stats'] = {
            'total': ContactMessage.objects.count(),
            'unread': ContactMessage.objects.filter(is_read=False).count(),
        }
        return context


class ContactMessageDetailDashboard(AdminRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'index_module/dashboard/contact_detail.html'
    context_object_name = 'msg'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save(update_fields=['is_read'])
        return response


def contact_message_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('sign_in_page')
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, 'پیام حذف شد.')
    return redirect('dashboard_contact_messages')


def contact_message_toggle_read(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'دسترسی غیرمجاز.')
        return redirect('sign_in_page')
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=['is_read'])
    messages.success(request, 'وضعیت پیام به‌روز شد.')
    return redirect(request.META.get('HTTP_REFERER', reverse('dashboard_contact_messages')))
