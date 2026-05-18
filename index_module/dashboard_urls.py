from django.urls import path
from . import views
from . import dashboard_views as dv
from subscriptions_module import dashboard_views as sub_dv

urlpatterns = [
    path('', views.main_dashboard, name='dashboard'),
    path('contact-messages/', dv.ContactMessageListDashboard.as_view(), name='dashboard_contact_messages'),
    path('contact-messages/<int:pk>/', dv.ContactMessageDetailDashboard.as_view(), name='dashboard_contact_detail'),
    path('contact-messages/<int:pk>/delete/', dv.contact_message_delete, name='dashboard_contact_delete'),
    path('contact-messages/<int:pk>/toggle-read/', dv.contact_message_toggle_read, name='dashboard_contact_toggle_read'),

    path('plans/', sub_dv.PlanListDashboard.as_view(), name='dashboard_plans'),
    path('plans/add/', sub_dv.PlanCreateDashboard.as_view(), name='dashboard_plan_add'),
    path('plans/<int:pk>/edit/', sub_dv.PlanUpdateDashboard.as_view(), name='dashboard_plan_edit'),

    path('orders/', sub_dv.OrderListDashboard.as_view(), name='dashboard_orders'),
    path('orders/<int:pk>/edit/', sub_dv.OrderUpdateDashboard.as_view(), name='dashboard_order_edit'),
    path('subscriptions/', sub_dv.SubscriptionListDashboard.as_view(), name='dashboard_subscriptions'),
    path('subscriptions/<int:pk>/edit/', sub_dv.SubscriptionUpdateDashboard.as_view(), name='dashboard_subscription_edit'),
    path('credits/', sub_dv.CreditTransactionListDashboard.as_view(), name='dashboard_credits'),
]
