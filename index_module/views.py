from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.contrib import messages
from account_module.decorators import admin_required
from .forms import ContactForm
from .site_info import SITE_INFO


def first_page(request):
    return render(request, 'index_module/main_page.html')


class AboutPageView(TemplateView):
    template_name = 'index_module/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site'] = SITE_INFO
        return context


class ContactPageView(View):
    template_name = 'index_module/contact.html'

    def get(self, request):
        initial = {}
        if request.user.is_authenticated:
            initial['name'] = request.user.get_full_name() or request.user.username or ''
            initial['email'] = request.user.email or ''
            initial['phone'] = getattr(request.user, 'phone_number', '') or ''
        return render(request, self.template_name, {
            'form': ContactForm(initial=initial),
            'site': SITE_INFO,
        })

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس می‌گیریم.',
            )
            return redirect('contact_page')
        messages.error(request, 'لطفاً خطاهای فرم را برطرف کنید و دوباره تلاش کنید.')
        return render(request, self.template_name, {
            'form': form,
            'site': SITE_INFO,
        })


@admin_required
def main_dashboard(request):
    from index_module.dashboard_services import (
        get_dashboard_charts_data,
        get_dashboard_stats,
        get_recent_contact_messages,
        get_recent_orders,
        get_recent_users,
    )
    stats = get_dashboard_stats()
    return render(request, 'index_module/index.html', {
        'stats': stats,
        'chart_data': get_dashboard_charts_data(14),
        'recent_messages': get_recent_contact_messages(),
        'recent_orders': get_recent_orders(),
        'recent_users': get_recent_users(),
    })
