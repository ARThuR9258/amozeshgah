from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.first_page, name='first_page'),
    path('about/', views.AboutPageView.as_view(), name='about_page'),
    path('contact/', views.ContactPageView.as_view(), name='contact_page'),
    path('dashboard/', include('index_module.dashboard_urls')),
]