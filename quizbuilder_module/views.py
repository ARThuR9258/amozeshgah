from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
from django.urls import reverse
from account_module.models import User
from account_module.decorators import AdminRequiredMixin
from .models import Quiz, QuizQuestion, UserQuiz, UserQuizQuestionAnswer, QuizQuestionChoice
from .helpers import UserQuizChoice

User = get_user_model()


class QuizListView(LoginRequiredMixin, ListView):
    """Display a list of all available quizzes"""
    model = Quiz
    template_name = 'quizbuilder_module/quiz_list.html'
    context_object_name = 'quizzes'
    ordering = ['-id']
    
    def get_queryset(self):
        # Get quizzes that are open and not expired
        now = timezone.now()
        return Quiz.objects.filter(
            status='open'
        ).annotate(
            question_count=Count('questions')
        ).prefetch_related('questions')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context


# In quizbuilder_module/views.py

class TakeQuizView(LoginRequiredMixin, View):
    MAX_FREE_ATTEMPTS = 2
    PAYMENT_AMOUNT = 99000  # 100,000 Tomans

    def check_exam_attempts(self, user):
        today = timezone.now().date()
        
        # Reset attempts if it's a new day
        if user.last_attempt_date != today:
            user.exam_attempts = 0
            user.last_attempt_date = today
            user.save(update_fields=['exam_attempts', 'last_attempt_date'])
        
        # Check if user has free attempts left
        if user.exam_attempts < self.MAX_FREE_ATTEMPTS:
            return True, None
            
        # Check if user has paid for additional attempts
        if user.has_paid_for_exam:
            return True, None
            
        # User needs to pay
        return False, {
            'can_take_exam': False,
            'needs_payment': True,
            'amount': self.PAYMENT_AMOUNT,
            'free_attempts_used': user.exam_attempts,
            'max_free_attempts': self.MAX_FREE_ATTEMPTS
        }

    def get(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related('questions', 'questions__choices'), 
            id=quiz_id, 
            status='open'
        )
        
        # Check exam attempts and payment status
        can_take_exam, payment_context = self.check_exam_attempts(request.user)
        if not can_take_exam:
            # Add quiz to the context
            context = {
                'quiz': quiz,
                **payment_context
            }
            return render(request, 'quizbuilder_module/payment_required.html', context)
        
        # Delete any existing incomplete attempts
        UserQuiz.objects.filter(
            user=request.user,
            quiz=quiz,
            status='pending'
        ).delete()
        
        # Create a new quiz attempt
        user_quiz = UserQuiz.objects.create(
            user=request.user,
            quiz=quiz,
            status='pending',
            start_time=timezone.now()
        )
        
        # Update user's exam attempts
        user = request.user
        user.exam_attempts += 1
        user.last_attempt_date = timezone.now().date()
        user.save(update_fields=['exam_attempts', 'last_attempt_date'])
        
        # Get all questions with their choices
        questions = quiz.questions.all().prefetch_related('choices')
        
        return render(request, 'quizbuilder_module/take_quiz.html', {
            'quiz': quiz,
            'questions': questions,
            'user_quiz': user_quiz,
            'remaining_attempts': max(0, self.MAX_FREE_ATTEMPTS - user.exam_attempts)
        })
    
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id, status='open')
        user_quiz = get_object_or_404(
            UserQuiz, 
            user=request.user, 
            quiz=quiz,
            status='pending'
        )
        
        # Calculate score
        score = 0
        total_questions = quiz.questions.count()
        
        with transaction.atomic():
            # Process each question
            for question in quiz.questions.prefetch_related('choices'):
                answer_id = request.POST.get(f'q{question.id}')
                if not answer_id:
                    continue
                    
                try:
                    selected_choice = question.choices.get(id=answer_id)
                    is_correct = selected_choice.is_answer
                    
                    # Save user's answer
                    UserQuizQuestionAnswer.objects.create(
                        user_quiz=user_quiz,
                        question=question,
                        answer=selected_choice
                    )
                    
                    # Update score if answer is correct
                    if is_correct:
                        score += question.score
                        
                except (QuizQuestionChoice.DoesNotExist, ValueError):
                    pass
            
            # Update user quiz status and score
            user_quiz.score = score
            user_quiz.status = 'done'
            user_quiz.save()
        
        return redirect('quizbuilder:quiz_result', quiz_id=quiz.id)


class QuizResultView(LoginRequiredMixin, TemplateView):
    """View for displaying quiz results"""
    template_name = 'quizbuilder_module/quiz_result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
        
        # Get the most recent attempt
        user_quiz = UserQuiz.objects.filter(
            user=self.request.user, 
            quiz=quiz
        ).order_by('-start_time').first()
        
        if not user_quiz:
            raise Http404("شما هنوز در این آزمون شرکت نکرده‌اید.")
        
        # Prepare questions data with user answers and choices
        questions_data = []
        user_answers = {}
        
        for answer in user_quiz.user_quiz_questions.select_related('question', 'answer'):
            user_answers[str(answer.question_id)] = str(answer.answer_id)
        
        # Get all questions with choices
        questions = quiz.questions.prefetch_related('choices')
        
        # Prepare questions data for template
        for question in questions:
            question_data = {
                'id': question.id,
                'description': question.description,
                'score': question.score,
                'choices': [],
                'user_answer': user_answers.get(str(question.id)),
                'is_correct': user_answers.get(str(question.id)) == str(question.correct_choice.id)
            }
            
            for choice in question.choices.all():
                question_data['choices'].append({
                    'id': choice.id,
                    'text': choice.text,
                    'is_answer': choice.is_answer,
                    'is_user_choice': user_answers.get(str(question.id)) == str(choice.id)
                })
            
            questions_data.append(question_data)
        
        # Calculate max possible score
        max_score = sum(question.score for question in questions)
        
        context.update({
            'quiz': quiz,
            'user_quiz': user_quiz,
            'questions_data': questions_data,
            'max_score': max_score,
            'show_answers': True
        })
        
        return context


@login_required
def process_payment(request, quiz_id):
    """
    Process payment for exam attempts beyond the free limit.
    In a real implementation, this would integrate with a payment gateway.
    For now, it simulates a successful payment.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, status='open')
    user = request.user
    
    # Verify user needs to pay
    if user.has_paid_for_exam:
        messages.warning(request, 'شما قبلاً پرداخت خود را انجام داده‌اید.')
        return redirect('quizbuilder:take_quiz', quiz_id=quiz.id)
    
    # In a real implementation, you would:
    # 1. Connect to a payment gateway (e.g., Zarinpal, IDPay, etc.)
    # 2. Create a payment request
    # 3. Redirect to the payment page
    # 4. Handle the callback/verification
    
    # For this example, we'll simulate a successful payment
    try:
        with transaction.atomic():
            # Update user's payment status
            user.has_paid_for_exam = True
            user.save(update_fields=['has_paid_for_exam'])
            
            # Log the payment (in a real app, you'd have a Payment model)
            # Payment.objects.create(user=user, amount=TakeQuizView.PAYMENT_AMOUNT, status='completed')
            
            messages.success(request, 'پرداخت با موفقیت انجام شد. اکنون می‌توانید در آزمون شرکت کنید.')
            return redirect('quizbuilder:take_quiz', quiz_id=quiz.id)
            
    except Exception as e:
        messages.error(request, f'خطا در پرداخت: {str(e)}')
        return redirect('quizbuilder:take_quiz', quiz_id=quiz.id)



class QuizListDashboard(AdminRequiredMixin, ListView):
    Model = Quiz
    template_name = 'quizbuilder_module/quiz_list_dashboard.html'
    context_object_name = 'quizs'

    def get_queryset(self):
        quizs = Quiz.objects.all()
        return quizs


    def get_context_data(self , **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class TextOfTheQuestionsDashboard(AdminRequiredMixin, ListView):
    model = QuizQuestion
    template_name = 'quizbuilder_module/text_of_the_questions_dashboard.html'
    context_object_name = 'quiz_texts'

    def get_queryset(self):
        quiz_texts = QuizQuestion.objects.all()
        return quiz_texts

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return context




class UserResponsesDashboard(AdminRequiredMixin, ListView):
    model = UserQuiz
    template_name = 'quizbuilder_module/user_responses_dashboard.html'
    context_object_name = 'user_responses'
    paginate_by = 5

    def get_queryset(self):
        user_responses = UserQuiz.objects.all()
        return user_responses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class ResponsesDashboard(AdminRequiredMixin, ListView):
    model = UserQuizQuestionAnswer
    template_name = 'quizbuilder_module/responses_dashboard.html'
    context_object_name = 'responses'
    paginate_by = 20

    def get_queryset(self):
        responses = UserQuizQuestionAnswer.objects.all()
        return responses

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OptionsDashboard(AdminRequiredMixin, ListView):
    model = QuizQuestionChoice
    template_name = 'quizbuilder_module/options_dashboard.html'
    context_object_name = 'options'
    paginate_by = 20

    def get_queryset(self):
        options = QuizQuestionChoice.objects.all()
        return options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
