# quizbuilder_module/urls.py
from django.urls import path
from . import views

app_name = 'quizbuilder'

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:quiz_id>/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('<int:quiz_id>/result/', views.QuizResultView.as_view(), name='quiz_result'),
]