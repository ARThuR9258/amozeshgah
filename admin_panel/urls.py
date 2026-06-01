from django.urls import path

from .views import (
    AnswerListView, AnswerTableView,
    CategoryCreateView, CategoryDeleteView, CategoryListView,
    CategoryTableView, CategoryUpdateView,
    ContactDeleteView, ContactDetailView, ContactListView,
    ContactTableView, ContactToggleReadView,
    CreditListView, CreditTableView,
    DashboardView,
    OrderListView, OrderTableView, OrderUpdateView,
    PlanCreateView, PlanDeleteView, PlanListView, PlanTableView, PlanUpdateView,
    QuestionCreateView, QuestionDeleteView, QuestionListView,
    QuestionTableView, QuestionUpdateView,
    SampleCreateView, SampleDeleteView, SampleListView,
    SampleTableView, SampleUpdateView,
    SessionDetailView, SessionListView, SessionTableView,
    SubscriptionListView, SubscriptionTableView, SubscriptionUpdateView,
    UserCreateView, UserDeleteView, UserListView, UserTableView, UserUpdateView,
)

app_name = 'admin_panel'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    path('users/', UserListView.as_view(), name='users_list'),
    path('users/table/', UserTableView.as_view(), name='users_table'),
    path('users/new/', UserCreateView.as_view(), name='users_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='users_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='users_delete'),

    path('samples/', SampleListView.as_view(), name='samples_list'),
    path('samples/table/', SampleTableView.as_view(), name='samples_table'),
    path('samples/new/', SampleCreateView.as_view(), name='samples_create'),
    path('samples/<int:pk>/edit/', SampleUpdateView.as_view(), name='samples_update'),
    path('samples/<int:pk>/delete/', SampleDeleteView.as_view(), name='samples_delete'),

    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('categories/table/', CategoryTableView.as_view(), name='categories_table'),
    path('categories/new/', CategoryCreateView.as_view(), name='categories_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='categories_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='categories_delete'),

    path('questions/', QuestionListView.as_view(), name='questions_list'),
    path('questions/table/', QuestionTableView.as_view(), name='questions_table'),
    path('questions/new/', QuestionCreateView.as_view(), name='questions_create'),
    path('questions/<int:pk>/edit/', QuestionUpdateView.as_view(), name='questions_update'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='questions_delete'),

    path('sessions/', SessionListView.as_view(), name='sessions_list'),
    path('sessions/table/', SessionTableView.as_view(), name='sessions_table'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='sessions_detail'),

    path('answers/', AnswerListView.as_view(), name='answers_list'),
    path('answers/table/', AnswerTableView.as_view(), name='answers_table'),

    path('plans/', PlanListView.as_view(), name='plans_list'),
    path('plans/table/', PlanTableView.as_view(), name='plans_table'),
    path('plans/new/', PlanCreateView.as_view(), name='plans_create'),
    path('plans/<int:pk>/edit/', PlanUpdateView.as_view(), name='plans_update'),
    path('plans/<int:pk>/delete/', PlanDeleteView.as_view(), name='plans_delete'),

    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('orders/table/', OrderTableView.as_view(), name='orders_table'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='orders_update'),

    path('subscriptions/', SubscriptionListView.as_view(), name='subscriptions_list'),
    path('subscriptions/table/', SubscriptionTableView.as_view(), name='subscriptions_table'),
    path('subscriptions/<int:pk>/edit/', SubscriptionUpdateView.as_view(), name='subscriptions_update'),

    path('credits/', CreditListView.as_view(), name='credits_list'),
    path('credits/table/', CreditTableView.as_view(), name='credits_table'),

    path('contacts/', ContactListView.as_view(), name='contacts_list'),
    path('contacts/table/', ContactTableView.as_view(), name='contacts_table'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contacts_detail'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='contacts_delete'),
    path('contacts/<int:pk>/toggle-read/', ContactToggleReadView.as_view(), name='contacts_toggle_read'),
]
