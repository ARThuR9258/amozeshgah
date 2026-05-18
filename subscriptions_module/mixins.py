"""
Mixin و دکوراتور کنترل دسترسی آزمون.
"""
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .services import QuizAccessResult, can_take_quiz


class QuizAccessMixin:
    """
    قبل از شروع آزمون، دسترسی کاربر را بررسی می‌کند.
    در صورت عدم دسترسی → هدایت به pricing با پیام مناسب.
    """

    access_denied_template = 'subscriptions_module/access_denied.html'
    redirect_to_pricing = True

    def check_quiz_access(self, user) -> QuizAccessResult:
        return can_take_quiz(user)

    def handle_access_denied(self, request, access: QuizAccessResult, quiz=None):
        messages.warning(request, access.message)
        if self.redirect_to_pricing:
            url = reverse('subscriptions:pricing')
            if quiz:
                url += f'?next=quiz&quiz_id={quiz.id}'
            return redirect(url)
        return None
