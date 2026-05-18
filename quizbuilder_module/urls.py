# quizbuilder_module/urls.py
from django.urls import path
from . import views
from . import dashboard_views as dv

app_name = 'quizbuilder'

urlpatterns = [
    path('dashboard/quizzes/add/', dv.QuizCreateDashboard.as_view(), name='dashboard_quiz_add'),
    path('dashboard/quizzes/<int:pk>/edit/', dv.QuizUpdateDashboard.as_view(), name='dashboard_quiz_edit'),
    path('dashboard/questions/add/', dv.QuizQuestionCreateDashboard.as_view(), name='dashboard_question_add'),
    path('dashboard/questions/<int:pk>/edit/', dv.QuizQuestionUpdateDashboard.as_view(), name='dashboard_question_edit'),
    path('dashboard/choices/add/', dv.QuizChoiceCreateDashboard.as_view(), name='dashboard_choice_add'),
    path('dashboard/choices/<int:pk>/edit/', dv.QuizChoiceUpdateDashboard.as_view(), name='dashboard_choice_edit'),
    path('dashboard/user-quiz/<int:pk>/', dv.UserQuizDetailDashboard.as_view(), name='dashboard_user_quiz_detail'),
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('share/<str:token>/', views.SharedResultView.as_view(), name='quiz_share_result'),
    path('<int:quiz_id>/save-answer/', views.quiz_save_answer, name='quiz_save_answer'),
    path('<int:quiz_id>/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('<int:quiz_id>/result/', views.QuizResultView.as_view(), name='quiz_result'),
    path('quiz-list-dashboard', views.QuizListDashboard.as_view(), name='quiz_list_dashboard'),
    path('text-quiz-list-dashboard', views.TextOfTheQuestionsDashboard.as_view(), name='text_quiz_list_dashboard'),
    path('user-response-dashboard', views.UserResponsesDashboard.as_view(), name='user_response_dashboard'),
    path('response-dashboard', views.ResponsesDashboard.as_view(), name='response_dashboard'),
    path('options-dashboard', views.OptionsDashboard.as_view(), name='options_dashboard'),
]