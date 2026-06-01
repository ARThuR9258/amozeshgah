from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.first_page, name='first_page'),
    path('about/', views.AboutPageView.as_view(), name='about_page'),
    path('contact/', views.ContactPageView.as_view(), name='contact_page'),
    path('dashboard/', include('admin_panel.urls')),
    # Legacy {% url 'dashboard' %} / dashboard_* names (old _master.html templates)
    path('dashboard/', include('admin_panel.legacy_urls')),
]