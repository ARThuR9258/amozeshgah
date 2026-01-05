from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Quiz, QuizQuestion, UserQuiz, UserQuizQuestionAnswer, QuizQuestionChoice
from .helpers import UserQuizChoice


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


class TakeQuizView(LoginRequiredMixin, View):
    """View for taking a quiz"""
    template_name = 'quizbuilder_module/take_quiz.html'
    
    def get(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related('questions', 'questions__choices'), 
            id=quiz_id, 
            status='open'
        )
        
        # Check if user has already taken this quiz
        user_quiz = UserQuiz.objects.filter(
            user=request.user,
            quiz=quiz
        ).first()
        
        if user_quiz and user_quiz.status != UserQuizChoice.PENDING:
            messages.info(request, 'شما قبلاً در این آزمون شرکت کرده‌اید.')
            return redirect('quizbuilder:quiz_result', quiz_id=quiz.id)
        
        # If no existing UserQuiz, create one
        if not user_quiz:
            user_quiz = UserQuiz.objects.create(
                user=request.user,
                quiz=quiz,
                status=UserQuizChoice.PENDING,
                start_time=timezone.now()
            )
        
        questions = quiz.questions.all().prefetch_related('choices')
        
        return render(request, self.template_name, {
            'quiz': quiz,
            'questions': questions,
            'user_quiz': user_quiz
        })
    
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id, status='open')
        user_quiz = get_object_or_404(
            UserQuiz, 
            user=request.user, 
            quiz=quiz,
            status=UserQuizChoice.PENDING
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
            user_quiz.status = UserQuizChoice.DONE
            user_quiz.save()
        
        messages.success(request, 'پاسخ‌های شما با موفقیت ثبت شد.')
        return redirect('quizbuilder:quiz_result', quiz_id=quiz.id)


class QuizResultView(LoginRequiredMixin, TemplateView):
    """View for displaying quiz results"""
    template_name = 'quizbuilder_module/quiz_result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = get_object_or_404(Quiz, id=self.kwargs['quiz_id'])
        user_quiz = get_object_or_404(
            UserQuiz, 
            user=self.request.user, 
            quiz=quiz
        )
        
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