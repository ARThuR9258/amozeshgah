"""منطق آزمون داینامیک: انتخاب سوال، جلسه، تایمر، نهایی‌سازی."""
from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from quizbuilder_module.helpers import (
    EXAM_DURATION_MINUTES,
    EXAM_QUESTION_COUNT,
    ExamSessionStatus,
    PASS_PERCENT,
)
from quizbuilder_module.models import ExamSession, Question, UserAnswer


class NotEnoughQuestionsError(Exception):
    pass


@dataclass
class ExamResultSummary:
    total: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    percent: int
    passed: bool
    wrong_questions: list


def pick_random_question_ids(count=EXAM_QUESTION_COUNT):
    ids = list(
        Question.objects.filter(is_active=True)
        .order_by('?')
        .values_list('id', flat=True)[:count]
    )
    if len(ids) < count:
        raise NotEnoughQuestionsError(
            f'حداقل {count} سوال فعال لازم است؛ الان {len(ids)} سوال فعال دارید.'
        )
    return ids


def get_active_session(user):
    return (
        ExamSession.objects.filter(
            user=user,
            status=ExamSessionStatus.IN_PROGRESS,
        )
        .order_by('-started_at')
        .first()
    )


def seconds_remaining(session: ExamSession) -> int:
    if not session.expires_at:
        return EXAM_DURATION_MINUTES * 60
    delta = (session.expires_at - timezone.now()).total_seconds()
    return max(0, int(delta))


def is_time_expired(session: ExamSession) -> bool:
    return seconds_remaining(session) <= 0


def get_session_questions(session: ExamSession):
    ids = session.question_ids or []
    if not ids:
        return Question.objects.none()
    preserved = {pk: idx for idx, pk in enumerate(ids)}
    qs = Question.objects.filter(id__in=ids, is_active=True)
    return sorted(qs, key=lambda q: preserved.get(q.id, 999))


def get_saved_answers_map(session: ExamSession) -> dict[str, int]:
    return {
        str(a.question_id): a.selected_choice
        for a in session.answers.exclude(selected_choice__isnull=True)
    }


@transaction.atomic
def create_exam_session(user) -> ExamSession:
    existing = get_active_session(user)
    if existing:
        return existing

    question_ids = pick_random_question_ids()
    now = timezone.now()
    session = ExamSession.objects.create(
        user=user,
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


def save_answer(session: ExamSession, question_id, choice_number) -> tuple[bool, str]:
    if session.status != ExamSessionStatus.IN_PROGRESS:
        return False, 'این آزمون قبلاً پایان یافته است.'
    if is_time_expired(session):
        return False, 'زمان آزمون تمام شده است.'

    try:
        choice_number = int(choice_number)
    except (TypeError, ValueError):
        return False, 'گزینه نامعتبر است.'
    if choice_number not in (1, 2, 3, 4):
        return False, 'گزینه نامعتبر است.'

    if question_id not in (session.question_ids or []):
        return False, 'سوال در این آزمون نیست.'

    question = Question.objects.filter(pk=question_id, is_active=True).first()
    if not question:
        return False, 'سوال نامعتبر است.'

    is_correct = choice_number == question.correct_answer
    UserAnswer.objects.update_or_create(
        session=session,
        question=question,
        defaults={
            'selected_choice': choice_number,
            'is_correct': is_correct,
            'answered_at': timezone.now(),
        },
    )
    return True, ''


def build_result_summary(session: ExamSession) -> ExamResultSummary:
    questions = get_session_questions(session)
    answers = {
        a.question_id: a
        for a in session.answers.select_related('question').all()
    }
    correct = wrong = skipped = 0
    wrong_questions = []

    for q in questions:
        ans = answers.get(q.id)
        if not ans or ans.selected_choice is None:
            skipped += 1
            continue
        if ans.is_correct:
            correct += 1
        else:
            wrong += 1
            wrong_questions.append({
                'question': q,
                'selected': ans.selected_choice,
                'correct': q.correct_answer,
            })

    total = len(questions)
    percent = int(round((correct / total) * 100)) if total else 0
    passed = percent >= PASS_PERCENT

    return ExamResultSummary(
        total=total,
        correct_count=correct,
        wrong_count=wrong,
        skipped_count=skipped,
        percent=percent,
        passed=passed,
        wrong_questions=wrong_questions,
    )


@transaction.atomic
def finalize_exam_session(session: ExamSession, post_data=None) -> ExamSession:
    if session.status != ExamSessionStatus.IN_PROGRESS:
        return session

    if post_data:
        for qid in session.question_ids or []:
            key = f'q{qid}'
            raw = post_data.get(key)
            if raw:
                save_answer(session, qid, raw)

    if is_time_expired(session) and session.status == ExamSessionStatus.IN_PROGRESS:
        session.status = ExamSessionStatus.EXPIRED

    summary = build_result_summary(session)
    now = timezone.now()
    spent = int((now - session.started_at).total_seconds()) if session.started_at else 0

    session.correct_count = summary.correct_count
    session.wrong_count = summary.wrong_count
    session.skipped_count = summary.skipped_count
    session.percent = summary.percent
    session.passed = summary.passed
    session.finished_at = now
    session.time_spent_seconds = spent
    if session.status == ExamSessionStatus.IN_PROGRESS:
        session.status = (
            ExamSessionStatus.EXPIRED if is_time_expired(session)
            else ExamSessionStatus.COMPLETED
        )
    session.save(
        update_fields=[
            'status', 'correct_count', 'wrong_count', 'skipped_count',
            'percent', 'passed', 'finished_at', 'time_spent_seconds',
        ]
    )
    return session


def expire_session_if_needed(session: ExamSession) -> ExamSession | None:
    """اگر وقت تمام شده، نهایی‌سازی و برگرداندن session."""
    if session.status == ExamSessionStatus.IN_PROGRESS and is_time_expired(session):
        return finalize_exam_session(session)
    return None
