from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('sign-up/', views.SignUpView.as_view(), name='sign_up_page' ),
    path('sign-in/', views.LoginView.as_view(), name='sign_in_page' ),
    path('log-out/', views.logout_view, name='log_out_page' ),
    path('panel/', views.user_panel_view, name='user_panel_page'),
    
    # Password reset URLs
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot-password/done/', views.forgot_password_done, name='forgot_password_done'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)