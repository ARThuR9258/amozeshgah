from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from account_module.decorators import AdminRequiredMixin
from amozeshga.dashboard_form_mixins import dashboard_form_context, form_has_files
from quizbuilder_module.forms import (
    QuizDashboardForm,
    QuizQuestionChoiceDashboardForm,
    QuizQuestionDashboardForm,
    UserQuizDashboardForm,
)
from quizbuilder_module.models import Quiz, QuizQuestion, QuizQuestionChoice, UserQuiz, UserQuizQuestionAnswer


class _DashboardFormMixin(AdminRequiredMixin):
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

    def _page_context(self):
        raise NotImplementedError


class QuizCreateDashboard(_DashboardFormMixin, CreateView):
    model = Quiz
    form_class = QuizDashboardForm
    success_url = reverse_lazy('quizbuilder:quiz_list_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title='آزمون جدید',
            page_heading='افزودن آزمون جدید',
            page_icon='clipboard-list',
            page_subtitle='تعریف آزمون برای شرکت کاربران',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:quiz_list_dashboard'), 'label': 'آزمون‌ها'},
                {'url': None, 'label': 'جدید'},
            ],
            cancel_url=reverse('quizbuilder:quiz_list_dashboard'),
            submit_label='ایجاد آزمون',
            form_section_title='مشخصات آزمون',
            form_section_icon='clipboard-list',
        )

    def form_valid(self, form):
        messages.success(self.request, 'آزمون با موفقیت ایجاد شد.')
        return super().form_valid(form)


class QuizUpdateDashboard(_DashboardFormMixin, UpdateView):
    model = Quiz
    form_class = QuizDashboardForm
    success_url = reverse_lazy('quizbuilder:quiz_list_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title=f'ویرایش {self.object.title}',
            page_heading=f'ویرایش آزمون «{self.object.title}»',
            page_icon='pen',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:quiz_list_dashboard'), 'label': 'آزمون‌ها'},
                {'url': None, 'label': 'ویرایش'},
            ],
            cancel_url=reverse('quizbuilder:quiz_list_dashboard'),
            form_section_title='ویرایش آزمون',
        )

    def form_valid(self, form):
        messages.success(self.request, 'آزمون به‌روزرسانی شد.')
        return super().form_valid(form)


class QuizQuestionCreateDashboard(_DashboardFormMixin, CreateView):
    model = QuizQuestion
    form_class = QuizQuestionDashboardForm
    success_url = reverse_lazy('quizbuilder:text_quiz_list_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title='سوال جدید',
            page_heading='افزودن سوال آزمون',
            page_icon='question-circle',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:text_quiz_list_dashboard'), 'label': 'سوالات'},
                {'url': None, 'label': 'جدید'},
            ],
            cancel_url=reverse('quizbuilder:text_quiz_list_dashboard'),
            submit_label='ایجاد سوال',
            form_section_title='متن و گزینه‌های سوال',
        )

    def form_valid(self, form):
        messages.success(self.request, 'سوال با موفقیت ایجاد شد.')
        return super().form_valid(form)


class QuizQuestionUpdateDashboard(_DashboardFormMixin, UpdateView):
    model = QuizQuestion
    form_class = QuizQuestionDashboardForm
    success_url = reverse_lazy('quizbuilder:text_quiz_list_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title='ویرایش سوال',
            page_heading='ویرایش سوال آزمون',
            page_icon='pen',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:text_quiz_list_dashboard'), 'label': 'سوالات'},
                {'url': None, 'label': 'ویرایش'},
            ],
            cancel_url=reverse('quizbuilder:text_quiz_list_dashboard'),
            form_section_title='ویرایش سوال',
        )

    def form_valid(self, form):
        messages.success(self.request, 'سوال به‌روزرسانی شد.')
        return super().form_valid(form)


class QuizChoiceCreateDashboard(_DashboardFormMixin, CreateView):
    model = QuizQuestionChoice
    form_class = QuizQuestionChoiceDashboardForm
    success_url = reverse_lazy('quizbuilder:options_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title='گزینه جدید',
            page_heading='افزودن گزینه پاسخ',
            page_icon='list',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:options_dashboard'), 'label': 'گزینه‌ها'},
                {'url': None, 'label': 'جدید'},
            ],
            cancel_url=reverse('quizbuilder:options_dashboard'),
            submit_label='ایجاد گزینه',
            form_section_title='مشخصات گزینه',
        )

    def form_valid(self, form):
        messages.success(self.request, 'گزینه با موفقیت ایجاد شد.')
        return super().form_valid(form)


class QuizChoiceUpdateDashboard(_DashboardFormMixin, UpdateView):
    model = QuizQuestionChoice
    form_class = QuizQuestionChoiceDashboardForm
    success_url = reverse_lazy('quizbuilder:options_dashboard')

    def _page_context(self):
        return dashboard_form_context(
            page_title='ویرایش گزینه',
            page_heading='ویرایش گزینه پاسخ',
            page_icon='pen',
            breadcrumbs=[
                {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
                {'url': reverse('quizbuilder:options_dashboard'), 'label': 'گزینه‌ها'},
                {'url': None, 'label': 'ویرایش'},
            ],
            cancel_url=reverse('quizbuilder:options_dashboard'),
            form_section_title='ویرایش گزینه',
        )

    def form_valid(self, form):
        messages.success(self.request, 'گزینه به‌روزرسانی شد.')
        return super().form_valid(form)


class UserQuizDetailDashboard(AdminRequiredMixin, DetailView):
    model = UserQuiz
    template_name = 'quizbuilder_module/dashboard/user_quiz_detail.html'
    context_object_name = 'user_quiz'

    def get_queryset(self):
        return UserQuiz.objects.select_related('user', 'quiz')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uq = self.object
        context['answers'] = (
            UserQuizQuestionAnswer.objects.filter(user_quiz=uq)
            .select_related('question', 'answer')
            .order_by('question_id')
        )
        context['edit_form'] = UserQuizDashboardForm(instance=uq)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = UserQuizDashboardForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, 'پاسخنامه به‌روزرسانی شد.')
            return self.get(request, *args, **kwargs)
        context = self.get_context_data(object=self.object)
        context['edit_form'] = form
        return self.render_to_response(context)
