from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from account_module.decorators import AdminRequiredMixin
from amozeshga.dashboard_form_mixins import dashboard_form_context, form_has_files
from sample_questions.forms import SampleQuestionDashboardForm
from sample_questions.models import SampleQuestion


class _SampleFormMixin(AdminRequiredMixin):
    template_name = 'layout/dashboard/model_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs['files'] = self.request.FILES
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form') or self.get_form()
        context.update(self._page_context())
        context['form_enctype'] = (
            'multipart/form-data' if form_has_files(form) else 'application/x-www-form-urlencoded'
        )
        return context


class SampleQuestionCreateDashboard(_SampleFormMixin, CreateView):
    model = SampleQuestion
    form_class = SampleQuestionDashboardForm
    success_url = reverse_lazy('sample_questions:question_list_dashboard_page')

    def _page_context(self):
        return dashboard_form_context(
            page_title='افزودن PDF',
            page_heading='افزودن نمونه سوال PDF',
            page_icon='file-pdf',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('sample_questions:question_list_dashboard_page'), 'label': 'نمونه سوالات'},
                {'url': None, 'label': 'جدید'},
            ],
            cancel_url=reverse('sample_questions:question_list_dashboard_page'),
            submit_label='آپلود و ذخیره',
            form_section_title='فایل و مشخصات',
            form_section_icon='file-pdf',
        )

    def form_valid(self, form):
        messages.success(self.request, 'نمونه سوال با موفقیت اضافه شد.')
        return super().form_valid(form)


class SampleQuestionUpdateDashboard(_SampleFormMixin, UpdateView):
    model = SampleQuestion
    form_class = SampleQuestionDashboardForm
    success_url = reverse_lazy('sample_questions:question_list_dashboard_page')

    def _page_context(self):
        return dashboard_form_context(
            page_title=f'ویرایش {self.object.title}',
            page_heading=f'ویرایش «{self.object.title}»',
            page_icon='pen',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('sample_questions:question_list_dashboard_page'), 'label': 'نمونه سوالات'},
                {'url': None, 'label': 'ویرایش'},
            ],
            cancel_url=reverse('sample_questions:question_list_dashboard_page'),
            form_section_title='ویرایش نمونه سوال',
        )

    def form_valid(self, form):
        messages.success(self.request, 'نمونه سوال به‌روزرسانی شد.')
        return super().form_valid(form)
