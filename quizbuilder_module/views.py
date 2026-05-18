from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.urls import reverse
from account_module.models import User
from account_module.decorators import AdminRequiredMixin
from .models import Quiz, QuizQuestion, UserQuiz, UserQuizQuestionAnswer, QuizQuestionChoice
from .helpers import UserQuizChoice
from subscriptions_module.mixins import QuizAccessMixin
from subscriptions_module.services import consume_quiz_access
from amozeshga.browse_helpers import (
    get_search_query,
    get_sort,
    get_filter,
    build_query_string,
    has_active_filters,
)

User = get_user_model()

QUIZ_SORT_MAP = {
    'newest': '-id',
    'title': 'title',
    'title_desc': '-title',
    'questions': '-question_count',
    'duration_asc': 'time',
    'duration_desc': '-time',
}

QUIZ_SORT_OPTIONS = [
    ('newest', 'جدیدترین'),
    ('title', 'عنوان (الفبا)'),
    ('title_desc', 'عنوان (معکوس)'),
    ('questions', 'بیشترین سوال'),
    ('duration_asc', 'کوتاه‌ترین زمان'),
    ('duration_desc', 'طولانی‌ترین زمان'),
]

QUIZ_FILTER_OPTIONS = [
    {'value': 'all', 'label': 'همه', 'icon': 'fa-list'},
    {'value': 'timed', 'label': 'زمان‌دار', 'icon': 'fa-clock'},
    {'value': 'untimed', 'label': 'بدون محدودیت', 'icon': 'fa-infinity'},
]


class QuizListView(LoginRequiredMixin, ListView):
    """Display a list of all available quizzes"""
    model = Quiz
    template_name = 'quizbuilder_module/quiz_list.html'
    context_object_name = 'quizzes'
    ordering = ['-id']

    def get_queryset(self):
        qs = Quiz.objects.filter(status='open').annotate(
            question_count=Count('questions')
        )

        q = get_search_query(self.request)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(desc__icontains=q))

        filter_val = get_filter(self.request, 'all')
        if filter_val == 'timed':
            qs = qs.filter(time__isnull=False, time__gt=0)
        elif filter_val == 'untimed':
            qs = qs.filter(Q(time__isnull=True) | Q(time=0))

        sort_key = get_sort(self.request, 'newest')
        order = QUIZ_SORT_MAP.get(sort_key, '-id')
        return qs.order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = get_search_query(self.request)
        context['sort'] = get_sort(self.request, 'newest')
        context['filter'] = get_filter(self.request, 'all')
        context['sort_options'] = QUIZ_SORT_OPTIONS
        context['filter_options'] = QUIZ_FILTER_OPTIONS
        context['browse_query'] = build_query_string(self.request)
        context['has_active_filters'] = has_active_filters(self.request, filter_default='all')
        context['toolbar_id'] = 'quizzes'
        context['search_placeholder'] = 'جستجو در عنوان یا توضیحات آزمون...'
        if context.get('is_paginated'):
            context['result_count'] = context['page_obj'].paginator.count
        else:
            context['result_count'] = len(context['quizzes'])
        context['total_active_count'] = Quiz.objects.filter(status='open').count()
        return context


# In quizbuilder_module/views.py

class TakeQuizView(LoginRequiredMixin, QuizAccessMixin, View):
    """شروع یا ادامه آزمون — تایمر، ذخیره خودکار، از سرگیری."""

    def get(self, request, quiz_id):
        from .quiz_services import get_saved_answers_map, is_time_expired, seconds_remaining

        quiz = get_object_or_404(
            Quiz.objects.prefetch_related('questions', 'questions__choices'),
            id=quiz_id,
            status='open',
        )

        pending = UserQuiz.objects.filter(
            user=request.user,
            quiz=quiz,
            status=UserQuizChoice.PENDING,
        ).first()

        if pending and is_time_expired(pending, quiz):
            from .quiz_services import finalize_user_quiz
            finalize_user_quiz(pending, quiz)
            messages.info(request, 'زمان آزمون به پایان رسید. نتیجه ثبت شد.')
            return redirect('quizbuilder:quiz_result', quiz_id=quiz.id)

        if pending:
            user_quiz = pending
            access = self.check_quiz_access(request.user)
        else:
            access = self.check_quiz_access(request.user)
            if not access.allowed:
                return self.handle_access_denied(request, access, quiz=quiz)
            user_quiz = UserQuiz.objects.create(
                user=request.user,
                quiz=quiz,
                status=UserQuizChoice.PENDING,
                start_time=timezone.now(),
            )
            consume_quiz_access(request.user, access.access_type)
            request.user.refresh_from_db()

        questions = quiz.questions.all().prefetch_related('choices')
        saved_answers = get_saved_answers_map(user_quiz)
        time_left = seconds_remaining(user_quiz, quiz)

        return render(request, 'quizbuilder_module/take_quiz.html', {
            'quiz': quiz,
            'questions': questions,
            'user_quiz': user_quiz,
            'quiz_access': access,
            'credits_remaining': request.user.credits,
            'saved_answers': saved_answers,
            'time_left_seconds': time_left if time_left is not None else 0,
            'has_time_limit': quiz.time and quiz.time > 0,
            'is_resume': bool(pending),
        })

    def post(self, request, quiz_id):
        from .quiz_services import finalize_user_quiz, is_time_expired

        quiz = get_object_or_404(
            Quiz.objects.prefetch_related('questions', 'questions__choices'),
            id=quiz_id,
            status='open',
        )
        user_quiz = get_object_or_404(
            UserQuiz,
            user=request.user,
            quiz=quiz,
            status=UserQuizChoice.PENDING,
        )

        if is_time_expired(user_quiz, quiz):
            messages.warning(request, 'زمان آزمون تمام شده بود؛ پاسخ‌های ذخیره‌شده ثبت شد.')

        finalize_user_quiz(user_quiz, quiz, post_data=request.POST)
        return redirect('quizbuilder:quiz_result', quiz_id=quiz.id)


@login_required
@require_POST
def quiz_save_answer(request, quiz_id):
    """ذخیره خودکار یک پاسخ (AJAX)."""
    import json
    from .quiz_services import save_question_answer, is_time_expired

    quiz = get_object_or_404(Quiz, id=quiz_id, status='open')
    user_quiz = get_object_or_404(
        UserQuiz,
        user=request.user,
        quiz=quiz,
        status=UserQuizChoice.PENDING,
    )

    if is_time_expired(user_quiz, quiz):
        return JsonResponse({'ok': False, 'expired': True, 'error': 'زمان آزمون تمام شده است.'})

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        question_id = request.POST.get('question_id')
        choice_id = request.POST.get('choice_id')
    else:
        question_id = payload.get('question_id')
        choice_id = payload.get('choice_id')

    ok, err = save_question_answer(user_quiz, question_id, choice_id)
    if not ok:
        return JsonResponse({'ok': False, 'error': err}, status=400)

    answered = user_quiz.user_quiz_questions.count()
    total = quiz.questions.count()
    return JsonResponse({
        'ok': True,
        'answered': answered,
        'total': total,
    })


def _build_questions_result_data(user_quiz, quiz):
    """داده سوالات برای صفحه نتیجه."""
    questions_data = []
    user_answers = {}
    for answer in user_quiz.user_quiz_questions.select_related('question', 'answer'):
        user_answers[str(answer.question_id)] = str(answer.answer_id)

    for question in quiz.questions.prefetch_related('choices'):
        correct = question.correct_choice
        ua = user_answers.get(str(question.id))
        is_correct = bool(ua and correct and ua == str(correct.id))
        is_skipped = not ua

        question_data = {
            'id': question.id,
            'description': question.description,
            'image': question.image.url if question.image else None,
            'score': question.score,
            'choices': [],
            'user_answer': ua,
            'is_correct': is_correct,
            'is_skipped': is_skipped,
        }
        for choice in question.choices.all():
            question_data['choices'].append({
                'id': choice.id,
                'text': choice.text,
                'image': choice.image.url if choice.image else None,
                'is_answer': choice.is_answer,
                'is_user_choice': ua == str(choice.id),
            })
        questions_data.append(question_data)
    return questions_data


class QuizResultView(LoginRequiredMixin, TemplateView):
    """نتیجه آزمون با تحلیل و لینک اشتراک."""
    template_name = 'quizbuilder_module/quiz_result.html'

    def get_context_data(self, **kwargs):
        from .quiz_services import build_analysis

        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])

        completed_statuses = (
            UserQuizChoice.DONE,
            UserQuizChoice.PASS,
            UserQuizChoice.FAIL,
        )
        user_quiz = (
            UserQuiz.objects.filter(
                user=self.request.user,
                quiz=quiz,
                status__in=completed_statuses,
            )
            .order_by('-finished_at', '-start_time')
            .first()
        )

        if not user_quiz:
            raise Http404('شما هنوز در این آزمون شرکت نکرده‌اید.')

        if not user_quiz.share_token:
            from .quiz_services import _generate_share_token
            user_quiz.share_token = _generate_share_token()
            user_quiz.save(update_fields=['share_token'])

        questions_data = _build_questions_result_data(user_quiz, quiz)
        analysis = build_analysis(user_quiz, quiz)

        share_url = ''
        if user_quiz.share_token:
            share_url = self.request.build_absolute_uri(
                reverse('quizbuilder:quiz_share_result', kwargs={'token': user_quiz.share_token})
            )

        context.update({
            'quiz': quiz,
            'user_quiz': user_quiz,
            'questions_data': questions_data,
            'max_score': analysis.max_score,
            'analysis': analysis,
            'show_answers': True,
            'share_url': share_url,
        })
        return context


class SharedResultView(TemplateView):
    """صفحه عمومی اشتراک نتیجه — بدون اطلاعات حساس."""
    template_name = 'quizbuilder_module/share_result.html'

    def get_context_data(self, **kwargs):
        from .quiz_services import get_shareable_result

        context = super().get_context_data(**kwargs)
        user_quiz = get_object_or_404(
            UserQuiz.objects.select_related('quiz'),
            share_token=self.kwargs['token'],
        )
        if user_quiz.status == UserQuizChoice.PENDING:
            raise Http404()
        if user_quiz.status == UserQuizChoice.DONE:
            from .quiz_services import build_analysis, PASS_PERCENT
            analysis = build_analysis(user_quiz, user_quiz.quiz)
            user_quiz.status = (
                UserQuizChoice.PASS if analysis.passed else UserQuizChoice.FAIL
            )
            if not user_quiz.finished_at:
                user_quiz.finished_at = user_quiz.start_time
            user_quiz.save(update_fields=['status', 'finished_at'])

        result = get_shareable_result(user_quiz)
        context['result'] = result
        context['user_quiz'] = user_quiz
        return context


class QuizListDashboard(AdminRequiredMixin, ListView):
    model = Quiz
    template_name = 'quizbuilder_module/quiz_list_dashboard.html'
    context_object_name = 'quizzes'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = Quiz.objects.all().order_by('-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(desc__icontains=q))
        status = self.request.GET.get('status')
        if status in ('open', 'close'):
            qs = qs.filter(status=status)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {
            'total': Quiz.objects.count(),
            'open': Quiz.objects.filter(status='open').count(),
            'closed': Quiz.objects.filter(status='close').count(),
        }
        return context


class TextOfTheQuestionsDashboard(AdminRequiredMixin, ListView):
    model = QuizQuestion
    template_name = 'quizbuilder_module/text_of_the_questions_dashboard.html'
    context_object_name = 'quiz_texts'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = QuizQuestion.objects.select_related('quiz').order_by('-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(quiz__title__icontains=q))
        quiz_id = self.request.GET.get('quiz')
        if quiz_id:
            qs = qs.filter(quiz_id=quiz_id)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['quiz_filter'] = self.request.GET.get('quiz', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['quiz_choices'] = Quiz.objects.all().order_by('title')
        context['stats'] = {'total': QuizQuestion.objects.count()}
        return context


class UserResponsesDashboard(AdminRequiredMixin, ListView):
    model = UserQuiz
    template_name = 'quizbuilder_module/user_responses_dashboard.html'
    context_object_name = 'user_responses'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = UserQuiz.objects.select_related('user', 'quiz').order_by('-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q)
                | Q(user__phone_number__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(quiz__title__icontains=q)
            )
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        from quizbuilder_module.helpers import UserQuizChoice

        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['status_choices'] = UserQuizChoice.CHOICES
        context['stats'] = {
            'total': UserQuiz.objects.count(),
            'pending': UserQuiz.objects.filter(status=UserQuizChoice.PENDING).count(),
            'done': UserQuiz.objects.filter(status=UserQuizChoice.DONE).count(),
        }
        return context


class ResponsesDashboard(AdminRequiredMixin, ListView):
    model = UserQuizQuestionAnswer
    template_name = 'quizbuilder_module/responses_dashboard.html'
    context_object_name = 'responses'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = UserQuizQuestionAnswer.objects.select_related(
            'user_quiz__user', 'user_quiz__quiz', 'question', 'answer'
        ).order_by('-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user_quiz__user__username__icontains=q)
                | Q(question__description__icontains=q)
                | Q(answer__text__icontains=q)
            )
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {'total': UserQuizQuestionAnswer.objects.count()}
        return context


class OptionsDashboard(AdminRequiredMixin, ListView):
    model = QuizQuestionChoice
    template_name = 'quizbuilder_module/options_dashboard.html'
    context_object_name = 'options'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = QuizQuestionChoice.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(text__icontains=q))
        correct = self.request.GET.get('correct')
        if correct == '1':
            qs = qs.filter(is_answer=True)
        elif correct == '0':
            qs = qs.filter(is_answer=False)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['correct_filter'] = self.request.GET.get('correct', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {
            'total': QuizQuestionChoice.objects.count(),
            'correct': QuizQuestionChoice.objects.filter(is_answer=True).count(),
        }
        return context
