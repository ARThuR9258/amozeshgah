from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.PricingView.as_view(), name='pricing'),
    path('checkout/<slug:plan_slug>/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
]
