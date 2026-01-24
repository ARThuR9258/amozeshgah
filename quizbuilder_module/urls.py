# quizbuilder_module/urls.py
from django.urls import path
from . import views

app_name = 'quizbuilder'

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:quiz_id>/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('<int:quiz_id>/result/', views.QuizResultView.as_view(), name='quiz_result'),
    path('<int:quiz_id>/process-payment/', views.process_payment, name='process_payment'),

    path('quiz-list-dashboard', views.QuizListDashboard.as_view(), name='quiz_list_dashboard'),
    path('text-quiz-list-dashboard', views.TextOfTheQuestionsDashboard.as_view(), name='text_quiz_list_dashboard'),
    path('user-response-dashboard', views.UserResponsesDashboard.as_view(), name='user_response_dashboard'),
    path('response-dashboard', views.ResponsesDashboard.as_view(), name='response_dashboard'),
    path('options-dashboard', views.OptionsDashboard.as_view(), name='options_dashboard'),
]