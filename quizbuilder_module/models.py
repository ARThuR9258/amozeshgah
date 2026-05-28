from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from quizbuilder_module.helpers import (
    ChoiceNumber,
    ExamSessionStatus,
    EXAM_DURATION_MINUTES,
    QuestionDifficulty,
)


class Category(models.Model):
    name = models.CharField(max_length=120, verbose_name='نام دسته')
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, verbose_name='شناسه')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField(verbose_name='متن سوال')
    image = models.ImageField(
        upload_to='exam/questions/',
        blank=True,
        null=True,
        verbose_name='تصویر سوال',
    )
    option_1 = models.CharField(max_length=500, verbose_name='گزینه ۱')
    option_2 = models.CharField(max_length=500, verbose_name='گزینه ۲')
    option_3 = models.CharField(max_length=500, verbose_name='گزینه ۳')
    option_4 = models.CharField(max_length=500, verbose_name='گزینه ۴')
    option_1_image = models.ImageField(
        upload_to='exam/options/',
        blank=True,
        null=True,
        verbose_name='تصویر گزینه ۱',
    )
    option_2_image = models.ImageField(
        upload_to='exam/options/',
        blank=True,
        null=True,
        verbose_name='تصویر گزینه ۲',
    )
    option_3_image = models.ImageField(
        upload_to='exam/options/',
        blank=True,
        null=True,
        verbose_name='تصویر گزینه ۳',
    )
    option_4_image = models.ImageField(
        upload_to='exam/options/',
        blank=True,
        null=True,
        verbose_name='تصویر گزینه ۴',
    )
    correct_answer = models.PositiveSmallIntegerField(
        choices=ChoiceNumber.CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='پاسخ صحیح',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='questions',
        verbose_name='دسته‌بندی',
    )
    difficulty = models.CharField(
        max_length=20,
        choices=QuestionDifficulty.CHOICES,
        default=QuestionDifficulty.MEDIUM,
        verbose_name='سطح سختی',
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین ویرایش')

    class Meta:
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'
        ordering = ['-id']

    def __str__(self):
        return self.text[:80]

    def get_option_text(self, number: int) -> str:
        return getattr(self, f'option_{number}', '') or ''

    def get_option_image(self, number: int):
        return getattr(self, f'option_{number}_image', None)

    def get_options_display(self):
        """لیست گزینه‌ها برای قالب: (شماره، متن، تصویر)."""
        items = []
        for num in range(1, 5):
            items.append({
                'number': num,
                'text': self.get_option_text(num),
                'image': self.get_option_image(num),
                'is_correct': num == self.correct_answer,
            })
        return items


class ExamSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        verbose_name='کاربر',
    )
    status = models.CharField(
        max_length=20,
        choices=ExamSessionStatus.CHOICES,
        default=ExamSessionStatus.IN_PROGRESS,
        verbose_name='وضعیت',
    )
    question_ids = models.JSONField(
        default=list,
        verbose_name='شناسه سوالات آزمون',
        help_text='۲۰ سوال انتخاب‌شده به صورت تصادفی',
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='شروع')
    expires_at = models.DateTimeField(verbose_name='پایان مهلت')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان اتمام')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='مدت (ثانیه)')
    correct_count = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد صحیح')
    wrong_count = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد غلط')
    skipped_count = models.PositiveSmallIntegerField(default=0, verbose_name='بدون پاسخ')
    percent = models.PositiveSmallIntegerField(default=0, verbose_name='درصد')
    passed = models.BooleanField(default=False, verbose_name='قبولی')

    class Meta:
        verbose_name = 'جلسه آزمون'
        verbose_name_plural = 'جلسات آزمون'
        ordering = ['-started_at']

    def __str__(self):
        return f'آزمون #{self.pk} — {self.user}'

    @property
    def total_questions(self):
        return len(self.question_ids or [])

    @property
    def is_in_progress(self):
        return self.status == ExamSessionStatus.IN_PROGRESS


class UserAnswer(models.Model):
    session = models.ForeignKey(
        ExamSession,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='جلسه آزمون',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='سوال',
    )
    selected_choice = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='گزینه انتخابی',
    )
    is_correct = models.BooleanField(null=True, blank=True, verbose_name='صحیح بود؟')
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان پاسخ')

    class Meta:
        verbose_name = 'پاسخ کاربر'
        verbose_name_plural = 'پاسخ‌های کاربر'
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'question'],
                name='unique_answer_per_session_question',
            ),
        ]

    def __str__(self):
        return f'{self.session_id} — Q{self.question_id}'
