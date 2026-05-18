"""
دکوراتور کنترل دسترسی آزمون برای function-based views.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .services import can_take_quiz


def quiz_access_required(view_func):
    """اگر کاربر مجاز به آزمون نباشد، به صفحه pricing هدایت شود."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access = can_take_quiz(request.user)
        if not access.allowed:
            messages.warning(request, access.message)
            return redirect('subscriptions:pricing')
        request.quiz_access = access
        return view_func(request, *args, **kwargs)

    return wrapper
