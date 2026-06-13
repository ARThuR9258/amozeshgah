from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from quizbuilder_module.exam_services import get_active_session
from quizbuilder_module.wrong_question_services import (
    NotEnoughWrongQuestionsError,
    create_wrong_practice_session,
    get_wrong_question_stats,
    get_wrong_questions_queryset,
)


class WrongQuestionsListView(LoginRequiredMixin, TemplateView):
    """صفحه سوالات اشتباه من."""

    template_name = 'quizbuilder_module/wrong_questions_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        stats = get_wrong_question_stats(user)
        practice_qs = get_wrong_questions_queryset(user, include_mastered=False)
        mastered_qs = get_wrong_questions_queryset(user, include_mastered=True).filter(
            is_mastered=True,
        )[:10]

        ctx.update({
            'stats': stats,
            'wrong_items': practice_qs,
            'mastered_preview': mastered_qs,
            'can_start_practice': practice_qs.exists(),
            'active_session': get_active_session(user),
        })
        return ctx


class WrongQuestionsExamStartView(LoginRequiredMixin, View):
    """شروع آزمون از سوالات اشتباه."""

    def post(self, request):
        active = get_active_session(request.user)
        if active:
            messages.info(request, 'ابتدا آزمون فعال خود را تمام کنید.')
            return redirect('quizbuilder:exam_take', session_id=active.pk)

        try:
            session = create_wrong_practice_session(request.user)
        except NotEnoughWrongQuestionsError as exc:
            messages.warning(request, str(exc))
            return redirect('wrong_questions_list')

        count = len(session.question_ids or [])
        messages.success(
            request,
            f'آزمون تمرین با {count} سوال اشتباه شروع شد.',
        )
        return redirect('quizbuilder:exam_take', session_id=session.pk)
