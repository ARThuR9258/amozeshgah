from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from account_module.forms import SignUpForm, LoginForm


# Create your views here.



class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'account_module/signup_page.html'
    success_url = reverse_lazy('first_page')


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
            
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('first_page')
        return super().get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('first_page')