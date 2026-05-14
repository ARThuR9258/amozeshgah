from django.urls import path
from . import views

app_name = 'sample_questions'

urlpatterns = [
    path('', views.SampleQuestionListView.as_view(), name='question_list'),
    path('download/<int:pk>/', views.download_question_paper, name='download_question_paper'),
    path('view/<int:pk>/', views.view_question_paper, name='view_question_paper'),
    path('question-list-dashboard', views.QuestionListDashboard.as_view(), name='question_list_dashboard_page'),
]
