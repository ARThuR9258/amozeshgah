from django.conf import settings


def subscription_context(request):
    return {
        'quiz_free_mode': getattr(settings, 'QUIZ_ACCESS_FREE_MODE', False),
    }
