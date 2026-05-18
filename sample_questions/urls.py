from django.urls import path
from . import views
from . import dashboard_views as dv

app_name = 'sample_questions'

urlpatterns = [
    path('', views.SampleQuestionListView.as_view(), name='question_list'),
    path('download/<int:pk>/', views.download_question_paper, name='download_question_paper'),
    path('view/<int:pk>/', views.view_question_paper, name='view_question_paper'),
    path('question-list-dashboard', views.QuestionListDashboard.as_view(), name='question_list_dashboard_page'),
    path('dashboard/add/', dv.SampleQuestionCreateDashboard.as_view(), name='dashboard_sample_add'),
    path('dashboard/<int:pk>/edit/', dv.SampleQuestionUpdateDashboard.as_view(), name='dashboard_sample_edit'),
]
