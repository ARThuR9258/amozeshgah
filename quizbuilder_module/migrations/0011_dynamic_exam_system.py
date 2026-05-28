# Generated manually — بازنویسی سیستم آزمون داینامیک

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizbuilder_module', '0010_remove_quiz_difficulty_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(name='UserQuizQuestionAnswer'),
        migrations.DeleteModel(name='UserQuiz'),
        migrations.DeleteModel(name='QuizQuestion'),
        migrations.DeleteModel(name='QuizQuestionChoice'),
        migrations.DeleteModel(name='Quiz'),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='نام دسته')),
                ('slug', models.SlugField(allow_unicode=True, max_length=120, unique=True, verbose_name='شناسه')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('display_order', models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'دسته‌بندی',
                'verbose_name_plural': 'دسته‌بندی‌ها',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='متن سوال')),
                ('image', models.ImageField(blank=True, null=True, upload_to='exam/questions/', verbose_name='تصویر سوال')),
                ('option_1', models.CharField(max_length=500, verbose_name='گزینه ۱')),
                ('option_2', models.CharField(max_length=500, verbose_name='گزینه ۲')),
                ('option_3', models.CharField(max_length=500, verbose_name='گزینه ۳')),
                ('option_4', models.CharField(max_length=500, verbose_name='گزینه ۴')),
                ('option_1_image', models.ImageField(blank=True, null=True, upload_to='exam/options/', verbose_name='تصویر گزینه ۱')),
                ('option_2_image', models.ImageField(blank=True, null=True, upload_to='exam/options/', verbose_name='تصویر گزینه ۲')),
                ('option_3_image', models.ImageField(blank=True, null=True, upload_to='exam/options/', verbose_name='تصویر گزینه ۳')),
                ('option_4_image', models.ImageField(blank=True, null=True, upload_to='exam/options/', verbose_name='تصویر گزینه ۴')),
                ('correct_answer', models.PositiveSmallIntegerField(
                    choices=[(1, 'گزینه ۱'), (2, 'گزینه ۲'), (3, 'گزینه ۳'), (4, 'گزینه ۴')],
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4),
                    ],
                    verbose_name='پاسخ صحیح',
                )),
                ('difficulty', models.CharField(
                    choices=[('easy', 'آسان'), ('medium', 'متوسط'), ('hard', 'سخت')],
                    default='medium',
                    max_length=20,
                    verbose_name='سطح سختی',
                )),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین ویرایش')),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='questions',
                    to='quizbuilder_module.category',
                    verbose_name='دسته‌بندی',
                )),
            ],
            options={
                'verbose_name': 'سوال',
                'verbose_name_plural': 'سوالات',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ExamSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('in_progress', 'در حال انجام'),
                        ('completed', 'پایان‌یافته'),
                        ('expired', 'زمان تمام شده'),
                    ],
                    default='in_progress',
                    max_length=20,
                    verbose_name='وضعیت',
                )),
                ('question_ids', models.JSONField(
                    default=list,
                    help_text='۲۰ سوال انتخاب‌شده به صورت تصادفی',
                    verbose_name='شناسه سوالات آزمون',
                )),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='شروع')),
                ('expires_at', models.DateTimeField(verbose_name='پایان مهلت')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='زمان اتمام')),
                ('time_spent_seconds', models.PositiveIntegerField(default=0, verbose_name='مدت (ثانیه)')),
                ('correct_count', models.PositiveSmallIntegerField(default=0, verbose_name='تعداد صحیح')),
                ('wrong_count', models.PositiveSmallIntegerField(default=0, verbose_name='تعداد غلط')),
                ('skipped_count', models.PositiveSmallIntegerField(default=0, verbose_name='بدون پاسخ')),
                ('percent', models.PositiveSmallIntegerField(default=0, verbose_name='درصد')),
                ('passed', models.BooleanField(default=False, verbose_name='قبولی')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='exam_sessions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='کاربر',
                )),
            ],
            options={
                'verbose_name': 'جلسه آزمون',
                'verbose_name_plural': 'جلسات آزمون',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_choice', models.PositiveSmallIntegerField(
                    blank=True,
                    null=True,
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4),
                    ],
                    verbose_name='گزینه انتخابی',
                )),
                ('is_correct', models.BooleanField(blank=True, null=True, verbose_name='صحیح بود؟')),
                ('answered_at', models.DateTimeField(blank=True, null=True, verbose_name='زمان پاسخ')),
                ('question', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='user_answers',
                    to='quizbuilder_module.question',
                    verbose_name='سوال',
                )),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='answers',
                    to='quizbuilder_module.examsession',
                    verbose_name='جلسه آزمون',
                )),
            ],
            options={
                'verbose_name': 'پاسخ کاربر',
                'verbose_name_plural': 'پاسخ‌های کاربر',
            },
        ),
        migrations.AddConstraint(
            model_name='useranswer',
            constraint=models.UniqueConstraint(
                fields=('session', 'question'),
                name='unique_answer_per_session_question',
            ),
        ),
    ]
