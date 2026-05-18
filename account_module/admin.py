from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account_module.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'phone_number', 'first_name', 'last_name',
        'credits', 'is_premium', 'subscription_status', 'is_verified',
    )
    list_filter = ('is_premium', 'subscription_status', 'is_staff', 'is_verified')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اشتراک و اعتبار', {
            'fields': (
                'credits', 'is_premium', 'subscription_status',
                'exam_attempts', 'last_attempt_date', 'has_paid_for_exam',
            ),
        }),
    )