from django.urls import path

from . import views

app_name = 'seo'

urlpatterns = [
    path('guide/', views.GuideListView.as_view(), name='guide_list'),
    path('guide/<str:slug>/', views.GuideDetailView.as_view(), name='guide_detail'),
]
