from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    """
    Decorator to ensure only admin users (is_staff=True) can access the view.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'شما مجوز دسترسی به این صفحه را ندارید.')
            return redirect('first_page')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class AdminRequiredMixin:
    """
    Mixin for class-based views to ensure only admin users can access the view.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفاً ابتدا وارد شوید.')
            return redirect('sign_in_page')
        
        if not request.user.is_staff:
            messages.error(request, 'شما مجوز دسترسی به این صفحه را ندارید.')
            return redirect('first_page')
        
        return super().dispatch(request, *args, **kwargs)
