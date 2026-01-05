import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from quizbuilder_module.helpers import QUIZ_STATUS, UserQuizChoice, QuizStatusClass, UserQuizStatusClass
from quizbuilder_module.mixins import QuizStartedSmsMixin

User = get_user_model()


class Quiz(QuizStartedSmsMixin, models.Model):
    """ آزمون """
    title = models.CharField(verbose_name='عنوان', max_length=255)
    desc = models.TextField(verbose_name='توضیحات', max_length=500)
    status = models.CharField(verbose_name='وضعیت', default='open', choices=QUIZ_STATUS.CHOICES, max_length=50)
    time = models.PositiveIntegerField(verbose_name='مدت زمان آزمون (دقیقه)', null=True, blank=True)
    expire_time = models.DateTimeField(verbose_name='تاریخ پایان آزمون', null=True, blank=True)

    class Meta:
        verbose_name = 'آزمون'
        verbose_name_plural = 'آزمون ها'

    def __str__(self):
        return self.title or '---'

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if self.time:
    #         self.expire_time = self.created_at.togregorian() + relativedelta(minutes=self.time)
    #     super().save(*args, **kwargs)

    @property
    def get_status(self):
        return dict(QUIZ_STATUS.CHOICES).get(self.status, '')

    @property
    def get_status_class(self):
        return dict(QuizStatusClass.CHOICES).get(self.status, '')


class QuizQuestionChoice(models.Model):
    """ گزینه های سوال """
    text = models.CharField(
        max_length=256,
        verbose_name='متن جواب'
    )
    is_answer = models.BooleanField(
        default=False,
        verbose_name='جواب صحیح است؟'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text[:100]


class QuizQuestion(models.Model):
    """ سوالات آزمون """
    quiz = models.ForeignKey(
        to=Quiz,
        verbose_name='آزمون',
        on_delete=models.CASCADE,
        related_name="questions",
    )
    description = models.TextField(
        verbose_name='متن سوال'
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name='بارم'
    )
    choices = models.ManyToManyField(
        verbose_name='گزینه های سوال',
        to=QuizQuestionChoice,
    )

    def __str__(self):
        return f'{self.quiz}, {self.description[:100]}'

    @property
    def correct_choice(self):
        return self.choices.filter(is_answer=True).first()


class UserQuiz(models.Model):
    """ پاسخنامه کاربر """
    user = models.ForeignKey(
        to=User,
        related_name='quizzes',
        verbose_name='کاربر',
        on_delete=models.CASCADE,
    )
    quiz = models.ForeignKey(
        to=Quiz,
        verbose_name='آزمون',
        on_delete=models.CASCADE,
        related_name='user_quizzes',
    )
    status = models.CharField(
        verbose_name='وضعیت',
        default=UserQuizChoice.PENDING,
        choices=UserQuizChoice.CHOICES,
        max_length=255
    )
    start_time = models.DateTimeField(
        verbose_name='زمان شروع آزمون',
        null=True, blank=True
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name='نمره(بارم)'
    )

    def __str__(self):
        return f'{self.user}, {self.quiz}'

    @property
    def get_status(self):
        return dict(UserQuizChoice.CHOICES).get(self.status, '')

    @property
    def get_status_class(self):
        return dict(UserQuizStatusClass.CHOICES).get(self.status, '')




class UserQuizQuestionAnswer(models.Model):
    """ پاسخ های کاربر """
    user_quiz = models.ForeignKey(
        to=UserQuiz,
        on_delete=models.CASCADE,
        related_name='user_quiz_questions',
        verbose_name='پاسخنامه کاربر',
    )
    question = models.ForeignKey(
        to=QuizQuestion,
        verbose_name='سوال',
        on_delete=models.CASCADE,
    )
    answer = models.ForeignKey(
        to=QuizQuestionChoice,
        on_delete=models.CASCADE,
        verbose_name='پاسخ کاربر',
    )

    def __str__(self):
        return f'{self.user_quiz}, {self.answer}'

    @property
    def get_user(self):
        return self.user_quiz.user
