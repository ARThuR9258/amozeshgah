"""منطق جلسه آزمون: تایمر، ذخیره پاسخ، نهایی‌سازی و اشتراک."""
import secrets
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from quizbuilder_module.helpers import UserQuizChoice
from quizbuilder_module.models import Quiz, QuizQuestion, QuizQuestionChoice, UserQuiz, UserQuizQuestionAnswer

PASS_PERCENT = 60


@dataclass
class QuizAnalysis:
    total_questions: int
    answered_count: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    max_score: int
    score: int
    percent: int
    passed: bool


def get_max_score(quiz):
    return sum(q.score for q in quiz.questions.all())


def seconds_remaining(user_quiz, quiz):
    """ثانیه باقی‌مانده؛ None = نامحدود."""
    if not quiz.time or quiz.time <= 0:
        return None
    if not user_quiz.start_time:
        return quiz.time * 60
    elapsed = (timezone.now() - user_quiz.start_time).total_seconds()
    return max(0, int(quiz.time * 60 - elapsed))


def is_time_expired(user_quiz, quiz):
    remaining = seconds_remaining(user_quiz, quiz)
    return remaining is not None and remaining <= 0


def get_saved_answers_map(user_quiz):
    return {
        str(a.question_id): str(a.answer_id)
        for a in user_quiz.user_quiz_questions.all()
    }


def save_question_answer(user_quiz, question_id, choice_id):
    """ذخیره یا به‌روزرسانی یک پاسخ (برای autosave)."""
    if user_quiz.status != UserQuizChoice.PENDING:
        return False, 'این آزمون قبلاً ثبت شده است.'

    question = QuizQuestion.objects.filter(pk=question_id, quiz_id=user_quiz.quiz_id).first()
    if not question:
        return False, 'سوال نامعتبر است.'

    choice = question.choices.filter(pk=choice_id).first()
    if not choice:
        return False, 'گزینه نامعتبر است.'

    UserQuizQuestionAnswer.objects.update_or_create(
        user_quiz=user_quiz,
        question=question,
        defaults={'answer': choice},
    )
    return True, ''


def build_analysis(user_quiz, quiz):
    questions = list(quiz.questions.prefetch_related('choices'))
    saved = get_saved_answers_map(user_quiz)
    max_score = sum(q.score for q in questions)
    score = 0
    correct = wrong = answered = 0

    for q in questions:
        ans_id = saved.get(str(q.id))
        if not ans_id:
            continue
        answered += 1
        correct_choice = q.correct_choice
        if correct_choice and str(correct_choice.id) == ans_id:
            correct += 1
            score += q.score
        else:
            wrong += 1

    skipped = len(questions) - answered
    percent = int(round((score / max_score) * 100)) if max_score else 0
    passed = percent >= PASS_PERCENT if max_score else correct == len(questions)

    return QuizAnalysis(
        total_questions=len(questions),
        answered_count=answered,
        correct_count=correct,
        wrong_count=wrong,
        skipped_count=skipped,
        max_score=max_score,
        score=score,
        percent=percent,
        passed=passed,
    )


@transaction.atomic
def finalize_user_quiz(user_quiz, quiz, post_data=None):
    """
    محاسبه نمره، تعیین pass/fail، توکن اشتراک.
    post_data: QueryDict اختیاری برای ارسال نهایی فرم.
    """
    if user_quiz.status != UserQuizChoice.PENDING:
        return user_quiz

    if post_data:
        for question in quiz.questions.prefetch_related('choices'):
            answer_id = post_data.get(f'q{question.id}')
            if answer_id:
                try:
                    choice = question.choices.get(id=answer_id)
                    UserQuizQuestionAnswer.objects.update_or_create(
                        user_quiz=user_quiz,
                        question=question,
                        defaults={'answer': choice},
                    )
                except (QuizQuestionChoice.DoesNotExist, ValueError):
                    pass

    analysis = build_analysis(user_quiz, quiz)
    now = timezone.now()
    spent = 0
    if user_quiz.start_time:
        spent = int((now - user_quiz.start_time).total_seconds())

    user_quiz.score = analysis.score
    user_quiz.status = UserQuizChoice.PASS if analysis.passed else UserQuizChoice.FAIL
    user_quiz.finished_at = now
    user_quiz.time_spent_seconds = spent
    if not user_quiz.share_token:
        user_quiz.share_token = _generate_share_token()
    user_quiz.save(
        update_fields=['score', 'status', 'finished_at', 'time_spent_seconds', 'share_token']
    )
    return user_quiz


def _generate_share_token():
    for _ in range(10):
        token = secrets.token_urlsafe(12)
        if not UserQuiz.objects.filter(share_token=token).exists():
            return token
    return secrets.token_urlsafe(16)


def get_shareable_result(user_quiz):
    """داده نتیجه برای صفحه عمومی (بدون اطلاعات حساس)."""
    quiz = user_quiz.quiz
    analysis = build_analysis(user_quiz, quiz)
    return {
        'quiz_title': quiz.title,
        'score': analysis.score,
        'max_score': analysis.max_score,
        'percent': analysis.percent,
        'passed': analysis.passed,
        'correct_count': analysis.correct_count,
        'wrong_count': analysis.wrong_count,
        'skipped_count': analysis.skipped_count,
        'total_questions': analysis.total_questions,
        'finished_at': user_quiz.finished_at or user_quiz.start_time,
        'time_spent_seconds': user_quiz.time_spent_seconds,
        'status_label': user_quiz.get_status,
    }
