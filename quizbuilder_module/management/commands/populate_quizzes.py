from django.core.management.base import BaseCommand
from django.utils import timezone
from quizbuilder_module.models import Quiz, QuizQuestion, QuizQuestionChoice
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample quizzes and questions'

    def handle(self, *args, **options):
        # Create a superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='مدیر',
                last_name='سیستم'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))

        # Create sample quizzes
        quiz1 = Quiz.objects.create(
            title='آزمون نمونه ۱: دانش عمومی',
            desc='این یک آزمون نمونه برای تست سیستم است. شامل سوالات عمومی در زمینه‌های مختلف می‌باشد.',
            status='open',
            time=30,
            expire_time=timezone.now() + timezone.timedelta(days=7)
        )

        quiz2 = Quiz.objects.create(
            title='آزمون نمونه ۲: برنامه‌نویسی مقدماتی',
            desc='آزمون سنجش دانش مقدماتی برنامه‌نویسی',
            status='open',
            time=45,
            expire_time=timezone.now() + timezone.timedelta(days=14)
        )

        # Questions for Quiz 1
        q1_1 = QuizQuestion.objects.create(
            quiz=quiz1,
            description='پایتون یک زبان برنامه‌نویسی است که در کدام دهه ایجاد شد؟',
            score=5
        )
        
        # Choices for question 1
        QuizQuestionChoice.objects.bulk_create([
            QuizQuestionChoice(text='دهه ۱۹۷۰', is_answer=False),
            QuizQuestionChoice(text='دهه ۱۹۸۰', is_answer=False),
            QuizQuestionChoice(text='دهه ۱۹۹۰', is_answer=True),
            QuizQuestionChoice(text='دهه ۲۰۰۰', is_answer=False),
        ])
        q1_1.choices.set(QuizQuestionChoice.objects.order_by('-id')[:4])

        q1_2 = QuizQuestion.objects.create(
            quiz=quiz1,
            description='کدام یک از موارد زیر یک فریم‌ورک وب پایتون نیست؟',
            score=5
        )
        
        QuizQuestionChoice.objects.bulk_create([
            QuizQuestionChoice(text='Django', is_answer=False),
            QuizQuestionChoice(text='Flask', is_answer=False),
            QuizQuestionChoice(text='React', is_answer=True),
            QuizQuestionChoice(text='FastAPI', is_answer=False),
        ])
        q1_2.choices.set(QuizQuestionChoice.objects.order_by('-id')[:4])

        # Questions for Quiz 2
        q2_1 = QuizQuestion.objects.create(
            quiz=quiz2,
            description='کدام یک از موارد زیر یک نوع داده عددی در پایتون نیست؟',
            score=10
        )
        
        QuizQuestionChoice.objects.bulk_create([
            QuizQuestionChoice(text='int', is_answer=False),
            QuizQuestionChoice(text='float', is_answer=False),
            QuizQuestionChoice(text='decimal', is_answer=False),
            QuizQuestionChoice(text='string', is_answer=True),
        ])
        q2_1.choices.set(QuizQuestionChoice.objects.order_by('-id')[:4])

        q2_2 = QuizQuestion.objects.create(
            quiz=quiz2,
            description='برای تعریف یک تابع در پایتون از کدام کلمه کلیدی استفاده می‌شود؟',
            score=10
        )
        
        QuizQuestionChoice.objects.bulk_create([
            QuizQuestionChoice(text='func', is_answer=False),
            QuizQuestionChoice(text='def', is_answer=True),
            QuizQuestionChoice(text='function', is_answer=False),
            QuizQuestionChoice(text='define', is_answer=False),
        ])
        q2_2.choices.set(QuizQuestionChoice.objects.order_by('-id')[:4])

        q2_3 = QuizQuestion.objects.create(
            quiz=quiz2,
            description='کدام یک از موارد زیر برای ایجاد یک حلقه در پایتون استفاده نمی‌شود؟',
            score=10
        )
        
        QuizQuestionChoice.objects.bulk_create([
            QuizQuestionChoice(text='for', is_answer=False),
            QuizQuestionChoice(text='while', is_answer=False),
            QuizQuestionChoice(text='loop', is_answer=True),
            QuizQuestionChoice(text='None of the above', is_answer=False),
        ])
        q2_3.choices.set(QuizQuestionChoice.objects.order_by('-id')[:4])

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample quizzes and questions'))
