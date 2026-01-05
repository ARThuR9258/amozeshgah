class QUIZ_STATUS:
    OPEN = "open"
    CLOSE = "close"
    CHOICES = (
        (OPEN, "باز"),
        (CLOSE, "بسته"),
    )


class QuizStatusClass:
    OPEN = "open"
    CLOSE = "close"
    CHOICES = (
        (OPEN, 'success'),
        (CLOSE, 'danger'),
    )


class UserQuizChoice:
    PENDING = 'pending'
    DONE = 'done'
    PASS = 'pass'
    FAIL = 'fail'

    CHOICES = (
        (PENDING, 'در حال انجام'),
        (DONE, 'انجام شده'),
        (PASS, 'پاس شده'),
        (FAIL, 'رد شده')
    )


class UserQuizStatusClass:
    PENDING = 'pending'
    DONE = 'done'
    PASS = 'pass'
    FAIL = 'fail'
    CHOICES = (
        (PENDING, 'warning'),
        (DONE, 'warning'),
        (PASS, 'success'),
        (FAIL, 'danger'),
    )
