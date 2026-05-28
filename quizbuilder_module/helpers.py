"""ثابت‌ها و انتخاب‌های وضعیت آزمون داینامیک."""


class ExamSessionStatus:
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    EXPIRED = 'expired'

    CHOICES = [
        (IN_PROGRESS, 'در حال انجام'),
        (COMPLETED, 'پایان‌یافته'),
        (EXPIRED, 'زمان تمام شده'),
    ]


class QuestionDifficulty:
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

    CHOICES = [
        (EASY, 'آسان'),
        (MEDIUM, 'متوسط'),
        (HARD, 'سخت'),
    ]


class ChoiceNumber:
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4

    CHOICES = [
        (ONE, 'گزینه ۱'),
        (TWO, 'گزینه ۲'),
        (THREE, 'گزینه ۳'),
        (FOUR, 'گزینه ۴'),
    ]


EXAM_QUESTION_COUNT = 20
EXAM_DURATION_MINUTES = 30
PASS_PERCENT = 60
