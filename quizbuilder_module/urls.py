from django.urls import path

from . import dashboard_views as dv
from . import views

app_name = 'quizbuilder'

urlpatterns = [
    # عمومی
    path('', views.ExamHubView.as_view(), name='exam_hub'),
    path('', views.ExamHubView.as_view(), name='quiz_list'),
    path('start/', views.ExamStartView.as_view(), name='exam_start'),
    path('session/<int:session_id>/', views.ExamTakeView.as_view(), name='exam_take'),
    path(
        'session/<int:session_id>/save-answer/',
        views.exam_save_answer,
        name='exam_save_answer',
    ),
    path(
        'session/<int:session_id>/submit/',
        views.ExamTakeView.as_view(),
        name='exam_submit',
    ),
    path(
        'session/<int:session_id>/result/',
        views.ExamResultView.as_view(),
        name='exam_result',
    ),
    # داشبورد
    path('dashboard/categories/', views.CategoryListDashboard.as_view(), name='category_list_dashboard'),
    path('dashboard/categories/add/', dv.CategoryCreateDashboard.as_view(), name='dashboard_category_add'),
    path('dashboard/categories/<int:pk>/edit/', dv.CategoryUpdateDashboard.as_view(), name='dashboard_category_edit'),
    path('dashboard/questions/', views.QuestionListDashboard.as_view(), name='question_list_dashboard'),
    path('dashboard/questions/add/', dv.QuestionCreateDashboard.as_view(), name='dashboard_question_add'),
    path('dashboard/questions/<int:pk>/edit/', dv.QuestionUpdateDashboard.as_view(), name='dashboard_question_edit'),
    path('dashboard/sessions/', views.ExamSessionListDashboard.as_view(), name='exam_session_list_dashboard'),
    path('dashboard/sessions/<int:pk>/', dv.ExamSessionDetailDashboard.as_view(), name='dashboard_exam_session_detail'),
    # aliasها برای لینک‌های قدیمی داشبورد
    path('dashboard/responses/', views.ExamSessionListDashboard.as_view(), name='response_dashboard'),
    path('dashboard/options/', views.QuestionListDashboard.as_view(), name='options_dashboard'),
    # سازگاری با لینک‌های قدیمی
    path('quiz-list-dashboard', views.QuestionListDashboard.as_view(), name='quiz_list_dashboard'),
    path('text-quiz-list-dashboard', views.QuestionListDashboard.as_view(), name='text_quiz_list_dashboard'),
    path('user-response-dashboard', views.ExamSessionListDashboard.as_view(), name='user_response_dashboard'),
]
