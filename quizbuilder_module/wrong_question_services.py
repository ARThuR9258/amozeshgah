"""منطق سوالات اشتباه: ذخیره، آمار، آزمون تمرین، تسلط."""
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from quizbuilder_module.helpers import (
    EXAM_DURATION_MINUTES,
    EXAM_QUESTION_COUNT,
    ExamSessionStatus,
    ExamSessionType,
    MASTERED_CORRECT_STREAK,
)
from quizbuilder_module.models import ExamSession, Question, UserAnswer, WrongQuestion


class NotEnoughWrongQuestionsError(Exception):
    pass


@dataclass
class WrongQuestionStats:
    total: int
    mastered: int
    needs_practice: int
    progress_percent: int


def get_wrong_question_stats(user) -> WrongQuestionStats:
    agg = WrongQuestion.objects.filter(user=user).aggregate(
        total=Count('id'),
        mastered=Count('id', filter=Q(is_mastered=True)),
    )
    total = agg['total'] or 0
    mastered = agg['mastered'] or 0
    needs = total - mastered
    progress = int(round((mastered / total) * 100)) if total else 0
    return WrongQuestionStats(
        total=total,
        mastered=mastered,
        needs_practice=needs,
        progress_percent=progress,
    )


def get_wrong_questions_queryset(user, *, include_mastered: bool = False):
    qs = (
        WrongQuestion.objects.filter(user=user)
        .select_related('question', 'question__category')
    )
    if not include_mastered:
        qs = qs.filter(is_mastered=False, question__is_active=True)
    return qs.order_by('-last_wrong_at')


@transaction.atomic
def record_wrong_answer(user, question: Question, now=None) -> WrongQuestion:
    """ثبت یا به‌روزرسانی سوال اشتباه."""
    now = now or timezone.now()
    record, created = WrongQuestion.objects.select_for_update().get_or_create(
        user=user,
        question=question,
        defaults={
            'wrong_count': 1,
            'first_wrong_at': now,
            'last_wrong_at': now,
            'consecutive_correct': 0,
            'is_mastered': False,
        },
    )
    if not created:
        record.wrong_count += 1
        record.last_wrong_at = now
        record.consecutive_correct = 0
        record.is_mastered = False
        record.save(update_fields=[
            'wrong_count', 'last_wrong_at', 'consecutive_correct', 'is_mastered',
        ])
    return record


@transaction.atomic
def record_practice_correct(user, question: Question) -> WrongQuestion | None:
    """پاسخ صحیح در آزمون تمرین — سه بار پیاپی → تسلط."""
    record = (
        WrongQuestion.objects.select_for_update()
        .filter(user=user, question=question, is_mastered=False)
        .first()
    )
    if not record:
        return None
    record.consecutive_correct += 1
    update_fields = ['consecutive_correct']
    if record.consecutive_correct >= MASTERED_CORRECT_STREAK:
        record.is_mastered = True
        update_fields.append('is_mastered')
    record.save(update_fields=update_fields)
    return record


@transaction.atomic
def sync_wrong_questions_from_session(session: ExamSession) -> None:
    """بعد از پایان آزمون: ذخیره اشتباهات و به‌روزرسانی تسلط در تمرین."""
    if session.status not in (
        ExamSessionStatus.COMPLETED,
        ExamSessionStatus.EXPIRED,
    ):
        return

    answers = (
        session.answers
        .select_related('question')
        .filter(selected_choice__isnull=False)
    )
    is_practice = session.exam_type == ExamSessionType.WRONG_PRACTICE
    now = timezone.now()

    for ans in answers:
        if ans.is_correct:
            if is_practice:
                record_practice_correct(session.user, ans.question)
            continue
        record_wrong_answer(session.user, ans.question, now=now)


def pick_wrong_practice_question_ids(user, count=EXAM_QUESTION_COUNT) -> list[int]:
    ids = list(
        WrongQuestion.objects.filter(
            user=user,
            is_mastered=False,
            question__is_active=True,
        )
        .order_by('?')
        .values_list('question_id', flat=True)[:count]
    )
    if not ids:
        raise NotEnoughWrongQuestionsError(
            'سوالی برای تمرین ندارید. ابتدا در آزمون شرکت کنید.'
        )
    return ids


@transaction.atomic
def create_wrong_practice_session(user) -> ExamSession:
    existing = (
        ExamSession.objects.filter(
            user=user,
            status=ExamSessionStatus.IN_PROGRESS,
        )
        .order_by('-started_at')
        .first()
    )
    if existing:
        return existing

    question_ids = pick_wrong_practice_question_ids(user)
    now = timezone.now()
    session = ExamSession.objects.create(
        user=user,
        exam_type=ExamSessionType.WRONG_PRACTICE,
        status=ExamSessionStatus.IN_PROGRESS,
        question_ids=question_ids,
        expires_at=now + timedelta(minutes=EXAM_DURATION_MINUTES),
    )
    questions = Question.objects.filter(id__in=question_ids)
    UserAnswer.objects.bulk_create([
        UserAnswer(session=session, question=q)
        for q in questions
    ])
    return session
