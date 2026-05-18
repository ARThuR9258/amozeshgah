from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, View, ListView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import random
from rest_framework import viewsets
from rest_framework.viewsets import ViewSet

from .decorators import admin_required, AdminRequiredMixin
from .serializers import UserSerialize
from account_module.forms import SignUpForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, UserAddDashboardForm
from account_module.models import User


# Create your views here.



class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'account_module/signup_page.html'
    success_url = reverse_lazy('sign_in_page')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'ثبت‌نام شما با موفقیت انجام شد! خوش آمدید.')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'account_module/login_page.html'
    success_url = reverse_lazy('first_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        
        # Handle 'remember me' functionality
        if not form.cleaned_data.get('remember_me'):
            # Set session to expire when the browser is closed if 'remember me' is not checked
            self.request.session.set_expiry(0)
        
        messages.success(self.request, f'خوش آمدید {user.get_full_name() or user.email}! شما با موفقیت وارد شدید.')
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('first_page')
        return super().get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    messages.info(request, 'شما با موفقیت از سیستم خارج شدید. تا دیدار دوباره!')
    return redirect('first_page')


def user_panel_view(request):
    if not request.user.is_authenticated:
        return redirect('sign_in_page')

    from django.utils import timezone
    from subscriptions_module.services import (
        MAX_DAILY_FREE_ATTEMPTS,
        can_take_quiz,
        get_active_subscription,
    )
    from subscriptions_module.models import CreditTransaction
    from quizbuilder_module.models import UserQuiz

    user = request.user
    user.refresh_subscription_status()
    access = can_take_quiz(user)
    active_sub = get_active_subscription(user)

    free_used = user.exam_attempts if user.last_attempt_date == timezone.now().date() else 0
    free_left = max(0, MAX_DAILY_FREE_ATTEMPTS - free_used)

    status_labels = {
        'free': 'رایگان',
        'credit': 'اعتباری',
        'premium': 'پرمیوم',
        'expired': 'منقضی',
    }

    from subscriptions_module.models import PaymentOrder
    from quizbuilder_module.quiz_services import build_analysis, PASS_PERCENT
    import json

    completed_statuses = ('done', 'pass', 'fail')
    exam_history = (
        UserQuiz.objects.filter(user=user, status__in=completed_statuses)
        .select_related('quiz')
        .order_by('-finished_at', '-start_time')[:15]
    )
    history_enriched = []
    chart_labels = []
    chart_percents = []
    for uq in exam_history:
        analysis = build_analysis(uq, uq.quiz)
        history_enriched.append({
            'uq': uq,
            'percent': analysis.percent,
            'passed': analysis.passed or uq.status == 'pass',
        })
    for uq in reversed(exam_history[:10]):
        analysis = build_analysis(uq, uq.quiz)
        chart_labels.append(uq.quiz.title[:24])
        chart_percents.append(analysis.percent)

    pending_quiz = (
        UserQuiz.objects.filter(user=user, status='pending')
        .select_related('quiz')
        .order_by('-start_time')
        .first()
    )

    recent_transactions = (
        CreditTransaction.objects.filter(user=user)
        .order_by('-created_at')[:8]
    )
    recent_orders = (
        PaymentOrder.objects.filter(user=user)
        .select_related('plan')
        .order_by('-created_at')[:8]
    )

    total_pass = UserQuiz.objects.filter(user=user, status='pass').count()
    total_done = UserQuiz.objects.filter(user=user, status__in=completed_statuses).count()

    context = {
        'user': user,
        'full_name': user.get_full_name() or user.phone_number,
        'phone_number': user.phone_number,
        'email': user.email or '—',
        'is_active': 'فعال' if user.is_active else 'غیرفعال',
        'is_staff': user.is_staff,
        'date_joined': user.date_joined.strftime('%Y/%m/%d'),
        'last_login': user.last_login.strftime('%Y/%m/%d - %H:%M') if user.last_login else None,
        'subscription_label': status_labels.get(user.subscription_status, user.subscription_status),
        'active_subscription': active_sub,
        'subscription_expires': active_sub.expires_at.strftime('%Y/%m/%d') if active_sub and active_sub.expires_at else None,
        'plan_name': active_sub.plan.name if active_sub else None,
        'credits': user.credits,
        'free_attempts_left': free_left,
        'quiz_access': access,
        'total_quizzes_done': total_done,
        'total_pass': total_pass,
        'pass_percent_threshold': PASS_PERCENT,
        'exam_history': history_enriched,
        'pending_quiz': pending_quiz,
        'recent_transactions': recent_transactions,
        'recent_orders': recent_orders,
        'chart_labels_json': json.dumps(chart_labels, ensure_ascii=False),
        'chart_percents_json': json.dumps(chart_percents, ensure_ascii=False),
    }
    return render(request, 'account_module/user_panel.html', context)


class ForgotPasswordView(View):
    template_name = 'account_module/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('forgot_password_done')
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('first_page')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user = get_object_or_404(User, phone_number=phone_number)
            
            # Generate a 5-digit random code
            reset_code = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            
            # In a real application, you would send this code via SMS or email
            # For now, we'll store it in the session
            request.session['reset_code'] = reset_code
            request.session['reset_phone'] = phone_number
            request.session['reset_code_time'] = str(timezone.now())
            
            # Set session expiry to 30 minutes
            request.session.set_expiry(1800)
            
            # In a real app, you would send the code via SMS here
            # For testing purposes, we'll just print it to the console
            print(f"Reset code for {phone_number}: {reset_code}")
            
            messages.success(request, f'کد بازیابی برای شماره {phone_number} ارسال شد. لطفاً کد را وارد کنید.')
            return redirect('reset_password')
            
        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    template_name = 'account_module/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('sign_in_page')
    
    def get(self, request):
        if 'reset_code' not in request.session or 'reset_phone' not in request.session:
            messages.error(request, 'لطفاً ابتدا درخواست بازیابی رمز عبور دهید.')
            return redirect('forgot_password')
            
        # Check if code is expired (30 minutes)
        code_time = request.session.get('reset_code_time')
        if code_time:
            code_time = timezone.datetime.fromisoformat(code_time)
            if timezone.now() > code_time + timedelta(minutes=30):
                del request.session['reset_code']
                del request.session['reset_phone']
                del request.session['reset_code_time']
                messages.error(request, 'کد تایید منقضی شده است. لطفاً مجدداً اقدام کنید.')
                return redirect('forgot_password')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if 'reset_code' not in request.session or 'reset_phone' not in request.session:
            messages.error(request, 'لطفاً ابتدا درخواست بازیابی رمز عبور دهید.')
            return redirect('forgot_password')
            
        form = self.form_class(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            stored_code = request.session.get('reset_code')
            phone_number = request.session.get('reset_phone')
            
            if entered_code != stored_code:
                form.add_error('code', 'کد تایید نامعتبر است.')
                return render(request, self.template_name, {'form': form})
            
            try:
                user = User.objects.get(phone_number=phone_number)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Clean up the session
                del request.session['reset_code']
                del request.session['reset_phone']
                del request.session['reset_code_time']
                
                messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت. اکنون می‌توانید با رمز عبور جدید وارد شوید.')
                return redirect(self.success_url)
                
            except User.DoesNotExist:
                messages.error(request, 'کاربری با این مشخصات یافت نشد.')
                return redirect('forgot_password')
                
        return render(request, self.template_name, {'form': form})


def forgot_password_done(request):
    return render(request, 'account_module/forgot_password_done.html')




class UserListDashboard(AdminRequiredMixin, ListView):
    model = User
    template_name = 'account_module/users_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q
        from amozeshga.dashboard_list import build_pagination_query

        qs = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(phone_number__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        role = self.request.GET.get('role')
        if role == 'staff':
            qs = qs.filter(is_staff=True)
        elif role == 'verified':
            qs = qs.filter(is_verified=True, is_staff=False)
        sub = self.request.GET.get('sub')
        if sub == 'premium':
            qs = qs.filter(is_premium=True)
        elif sub == 'credit':
            qs = qs.filter(credits__gt=0, is_premium=False)
        active = self.request.GET.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['sub_filter'] = self.request.GET.get('sub', '')
        context['active_filter'] = self.request.GET.get('active', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['total_users'] = User.objects.count()
        context['stats'] = {
            'active': User.objects.filter(is_active=True).count(),
            'staff': User.objects.filter(is_staff=True).count(),
            'premium': User.objects.filter(is_premium=True).count(),
            'verified': User.objects.filter(is_verified=True).count(),
        }
        return context


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import admin_required
from .forms import UserEditDashboardForm
from amozeshga.dashboard_form_mixins import dashboard_form_context
from django.urls import reverse


@admin_required
def edit_user_dashboard(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditDashboardForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            display_name = user.get_full_name().strip() or user.username or user.phone_number
            messages.success(request, f'کاربر «{display_name}» به‌روزرسانی شد.')
            return redirect('user_list_dashboard_page')
    else:
        form = UserEditDashboardForm(instance=user)

    ctx = dashboard_form_context(
        page_title=f'ویرایش {user.get_full_name() or user.username}',
        page_heading=f'ویرایش کاربر «{user.get_full_name() or user.username}»',
        page_icon='user-pen',
        page_subtitle=user.phone_number or user.email or '',
        breadcrumbs=[
            {'url': reverse('dashboard'), 'label': None, 'icon': 'home'},
            {'url': reverse('user_list_dashboard_page'), 'label': 'کاربران'},
            {'url': None, 'label': 'ویرایش'},
        ],
        cancel_url=reverse('user_list_dashboard_page'),
        submit_label='ذخیره تغییرات',
        form_section_title='اطلاعات حساب',
        form_section_icon='user',
    )
    ctx['form'] = form
    ctx['form_enctype'] = 'application/x-www-form-urlencoded'
    return render(request, 'layout/dashboard/model_form.html', ctx)


@admin_required
def add_dashboard(request):
    if request.method == 'POST':
        form = UserAddDashboardForm(request.POST)
        if form.is_valid():
            user = form.save()
            display_name = user.get_full_name().strip() or user.username or user.phone_number
            messages.success(
                request,
                f'کاربر «{display_name}» با موفقیت ایجاد شد.',
            )
            next_action = request.POST.get('submit_action', 'list')
            if next_action == 'another':
                return redirect('add_user_dashboard')
            return redirect('user_list_dashboard_page')
    else:
        form = UserAddDashboardForm()

    return render(request, 'account_module/user_add_dashboard.html', {
        'form': form,
        'subscription_choices': User.SubscriptionStatus.choices,
    })


class UserViewSetApi(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerialize
