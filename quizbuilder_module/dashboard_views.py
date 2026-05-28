from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from account_module.decorators import AdminRequiredMixin
from quizbuilder_module.forms import CategoryForm, QuestionForm
from quizbuilder_module.models import Category, ExamSession, Question


class _DashboardFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = getattr(self, 'form_title', '')
        return context


class CategoryCreateDashboard(AdminRequiredMixin, _DashboardFormMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'quizbuilder_module/dashboard/form_page.html'
    success_url = reverse_lazy('quizbuilder:category_list_dashboard')
    form_title = 'دسته‌بندی جدید'


class CategoryUpdateDashboard(AdminRequiredMixin, _DashboardFormMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'quizbuilder_module/dashboard/form_page.html'
    success_url = reverse_lazy('quizbuilder:category_list_dashboard')
    form_title = 'ویرایش دسته‌بندی'


class QuestionCreateDashboard(AdminRequiredMixin, _DashboardFormMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quizbuilder_module/dashboard/question_form.html'
    success_url = reverse_lazy('quizbuilder:question_list_dashboard')
    form_title = 'سوال جدید'

    def form_valid(self, form):
        messages.success(self.request, 'سوال با موفقیت ذخیره شد.')
        return super().form_valid(form)


class QuestionUpdateDashboard(AdminRequiredMixin, _DashboardFormMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quizbuilder_module/dashboard/question_form.html'
    success_url = reverse_lazy('quizbuilder:question_list_dashboard')
    form_title = 'ویرایش سوال'

    def form_valid(self, form):
        messages.success(self.request, 'سوال به‌روزرسانی شد.')
        return super().form_valid(form)


class ExamSessionDetailDashboard(AdminRequiredMixin, DetailView):
    model = ExamSession
    template_name = 'quizbuilder_module/dashboard/exam_session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return ExamSession.objects.select_related('user')

    def get_context_data(self, **kwargs):
        from quizbuilder_module.exam_services import build_result_summary

        context = super().get_context_data(**kwargs)
        context['answers'] = self.object.answers.select_related('question').order_by('question_id')
        if self.object.status != 'in_progress':
            context['summary'] = build_result_summary(self.object)
        return context
