from django.urls import path
from . import views

app_name = 'sample_questions'

urlpatterns = [
    path('', views.SampleQuestionListView.as_view(), name='question_list'),
    path('download/<int:pk>/', views.download_question_paper, name='download_question_paper'),
]
