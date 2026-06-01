"""Backward-compatible URL names used by legacy dashboard templates (_master.html, etc.)."""
from django.urls import path

from .views import (
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactToggleReadView,
    CreditListView,
    DashboardView,
    OrderListView,
    OrderUpdateView,
    PlanCreateView,
    PlanListView,
    PlanUpdateView,
    SubscriptionListView,
    SubscriptionUpdateView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    path('contacts/', ContactListView.as_view(), name='dashboard_contact_messages'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='dashboard_contact_detail'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='dashboard_contact_delete'),
    path('contacts/<int:pk>/toggle-read/', ContactToggleReadView.as_view(), name='dashboard_contact_toggle_read'),

    path('plans/', PlanListView.as_view(), name='dashboard_plans'),
    path('plans/new/', PlanCreateView.as_view(), name='dashboard_plan_add'),
    path('plans/<int:pk>/edit/', PlanUpdateView.as_view(), name='dashboard_plan_edit'),

    path('orders/', OrderListView.as_view(), name='dashboard_orders'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='dashboard_order_edit'),

    path('subscriptions/', SubscriptionListView.as_view(), name='dashboard_subscriptions'),
    path('subscriptions/<int:pk>/edit/', SubscriptionUpdateView.as_view(), name='dashboard_subscription_edit'),

    path('credits/', CreditListView.as_view(), name='dashboard_credits'),
]
