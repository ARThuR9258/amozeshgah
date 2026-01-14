from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('sign-up/', views.SignUpView.as_view(), name='sign_up_page' ),
    path('sign-in/', views.LoginView.as_view(), name='sign_in_page' ),
    path('log-out/', views.logout_view, name='log_out_page' ),
    path('panel/', views.user_panel_view, name='user_panel_page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)