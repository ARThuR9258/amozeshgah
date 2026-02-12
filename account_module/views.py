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
        
    context = {
        'user': request.user,
        'full_name': request.user.get_full_name() or request.user.email,
        'email': request.user.email,
        'is_active': 'فعال' if request.user.is_active else 'غیرفعال',
        'is_staff': 'ادمین' if request.user.is_staff else 'کاربر عادی',
        'date_joined': request.user.date_joined.strftime('%Y/%m/%d - %H:%M')
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


    def get_queryset(self):
        users = User.objects.all()
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import admin_required

@admin_required
def add_dashboard(request):
    if request.method == 'POST':
        form = UserAddDashboardForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = form.cleaned_data['is_active']
            user.is_staff = form.cleaned_data['is_staff']
            user.is_verified = form.cleaned_data['is_verified']
            user.save()
            messages.success(request, f'کاربر {user.email} با موفقیت ایجاد شد.')
            return redirect('add_user_dashboard')
    else:
        form = UserAddDashboardForm()
    
    context = {
        'form': form,
        'title': 'افزودن کاربر جدید',
        'breadcrumbs': [
            {'title': 'داشبورد', 'url': reverse('dashboard')},
            {'title': 'مدیریت کاربران', 'url': reverse('user_list_dashboard_page')},
            {'title': 'افزودن کاربر جدید', 'url': ''},
        ]
    }
    return render(request, 'account_module/user_add_dashboard.html', context)


class UserViewSetApi(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerialize
