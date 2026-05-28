import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, TemplateView

from account_module.decorators import AdminRequiredMixin
from quizbuilder_module.exam_services import (
    NotEnoughQuestionsError,
    build_result_summary,
    create_exam_session,
    expire_session_if_needed,
    finalize_exam_session,
    get_active_session,
    get_saved_answers_map,
    get_session_questions,
    is_time_expired,
    save_answer,
    seconds_remaining,
)
from quizbuilder_module.helpers import (
    EXAM_DURATION_MINUTES,
    EXAM_QUESTION_COUNT,
    ExamSessionStatus,
    PASS_PERCENT,
)
from quizbuilder_module.models import Category, ExamSession, Question, UserAnswer
from subscriptions_module.mixins import QuizAccessMixin
from subscriptions_module.services import consume_quiz_access


class ExamHubView(LoginRequiredMixin, TemplateView):
    """صفحه آزمون — شروع جدید یا ادامه جلسه فعال."""

    template_name = 'quizbuilder_module/exam_hub.html'

    def get_context_data(self, **kwargs):
        from subscriptions_module.services import can_take_quiz

        context = super().get_context_data(**kwargs)
        active = get_active_session(self.request.user)
        active_count = Question.objects.filter(is_active=True).count()
        completed = ExamSession.objects.filter(
            user=self.request.user,
            status__in=(ExamSessionStatus.COMPLETED, ExamSessionStatus.EXPIRED),
        ).count()

        context.update({
            'active_session': active,
            'active_question_count': active_count,
            'can_start': active_count >= EXAM_QUESTION_COUNT,
            'required_questions': EXAM_QUESTION_COUNT,
            'exam_minutes': EXAM_DURATION_MINUTES,
            'quiz_access': can_take_quiz(self.request.user),
            'completed_exams': completed,
            'pass_percent': PASS_PERCENT,
        })
        return context


class ExamStartView(LoginRequiredMixin, QuizAccessMixin, View):
    """شروع آزمون — ۲۰ سوال تصادفی."""

    def post(self, request):
        active = get_active_session(request.user)
        if active:
            return redirect('quizbuilder:exam_take', session_id=active.pk)

        access = self.check_quiz_access(request.user)
        if not access.allowed:
            return self.handle_access_denied(request, access)

        try:
            session = create_exam_session(request.user)
        except NotEnoughQuestionsError as exc:
            messages.error(request, str(exc))
            return redirect('quizbuilder:exam_hub')

        consume_quiz_access(request.user, access.access_type)
        request.user.refresh_from_db()
        messages.success(request, 'آزمون شروع شد. ۳۰ دقیقه وقت دارید.')
        return redirect('quizbuilder:exam_take', session_id=session.pk)


class ExamTakeView(LoginRequiredMixin, View):
    """صفحه آزمون — نمایش سوالات و تایمر."""

    template_name = 'quizbuilder_module/exam_take.html'

    def get_session(self, request, session_id):
        session = get_object_or_404(
            ExamSession,
            pk=session_id,
            user=request.user,
        )
        if session.status != ExamSessionStatus.IN_PROGRESS:
            return None, redirect('quizbuilder:exam_result', session_id=session.pk)

        expired = expire_session_if_needed(session)
        if expired:
            messages.info(request, 'زمان آزمون تمام شد. نتیجه ثبت شد.')
            return None, redirect('quizbuilder:exam_result', session_id=session.pk)

        return session, None

    def get(self, request, session_id):
        session, redirect_resp = self.get_session(request, session_id)
        if redirect_resp:
            return redirect_resp

        questions = get_session_questions(session)
        saved_map = get_saved_answers_map(session)
        return render(request, self.template_name, {
            'session': session,
            'questions': questions,
            'saved_answers': saved_map,
            'saved_answers_json': json.dumps(saved_map, ensure_ascii=False),
            'time_left_seconds': seconds_remaining(session),
            'exam_minutes': EXAM_DURATION_MINUTES,
            'total_questions': session.total_questions,
            'save_answer_url': reverse(
                'quizbuilder:exam_save_answer',
                kwargs={'session_id': session.pk},
            ),
            'submit_url': reverse(
                'quizbuilder:exam_submit',
                kwargs={'session_id': session.pk},
            ),
        })

    def post(self, request, session_id):
        session = get_object_or_404(
            ExamSession,
            pk=session_id,
            user=request.user,
            status=ExamSessionStatus.IN_PROGRESS,
        )
        if is_time_expired(session):
            messages.warning(request, 'زمان آزمون تمام شده بود.')
        finalize_exam_session(session, post_data=request.POST)
        return redirect('quizbuilder:exam_result', session_id=session.pk)


@login_required
@require_POST
def exam_save_answer(request, session_id):
    session = get_object_or_404(
        ExamSession,
        pk=session_id,
        user=request.user,
        status=ExamSessionStatus.IN_PROGRESS,
    )
    if is_time_expired(session):
        finalize_exam_session(session)
        return JsonResponse({'ok': False, 'expired': True, 'error': 'زمان آزمون تمام شده است.'})

    try:
        payload = json.loads(request.body.decode('utf-8'))
        question_id = payload.get('question_id')
        choice_number = payload.get('choice_number')
    except (json.JSONDecodeError, UnicodeDecodeError):
        question_id = request.POST.get('question_id')
        choice_number = request.POST.get('choice_number')

    ok, err = save_answer(session, question_id, choice_number)
    if not ok:
        return JsonResponse({'ok': False, 'error': err}, status=400)

    answered = session.answers.exclude(selected_choice__isnull=True).count()
    return JsonResponse({
        'ok': True,
        'answered': answered,
        'total': session.total_questions,
    })


class ExamResultView(LoginRequiredMixin, TemplateView):
    template_name = 'quizbuilder_module/exam_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = get_object_or_404(
            ExamSession,
            pk=self.kwargs['session_id'],
            user=self.request.user,
        )
        summary = build_result_summary(session)
        context.update({
            'session': session,
            'summary': summary,
            'wrong_questions': summary.wrong_questions,
            'pass_percent': PASS_PERCENT,
        })
        return context

    def get(self, request, *args, **kwargs):
        session = get_object_or_404(
            ExamSession,
            pk=kwargs['session_id'],
            user=request.user,
        )
        if session.status == ExamSessionStatus.IN_PROGRESS and not is_time_expired(session):
            return redirect('quizbuilder:exam_take', session_id=session.pk)
        return super().get(request, *args, **kwargs)


# --- داشبورد ادمین ---

class CategoryListDashboard(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'quizbuilder_module/category_list_dashboard.html'
    context_object_name = 'categories'
    paginate_by = 20


class QuestionListDashboard(AdminRequiredMixin, ListView):
    model = Question
    template_name = 'quizbuilder_module/question_list_dashboard.html'
    context_object_name = 'questions'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q

        qs = Question.objects.select_related('category').order_by('-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(text__icontains=q) | Q(option_1__icontains=q))
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category_id=cat)
        active = self.request.GET.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['categories'] = Category.objects.filter(is_active=True)
        context['stats'] = {
            'total': Question.objects.count(),
            'active': Question.objects.filter(is_active=True).count(),
        }
        return context


class ExamSessionListDashboard(AdminRequiredMixin, ListView):
    model = ExamSession
    template_name = 'quizbuilder_module/exam_session_list_dashboard.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        return ExamSession.objects.select_related('user').order_by('-started_at')
