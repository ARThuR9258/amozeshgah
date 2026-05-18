from django.contrib import admin

from .models import CreditTransaction, PaymentOrder, SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'credits_amount', 'is_popular', 'is_active', 'display_order')
    list_filter = ('plan_type', 'is_active', 'is_popular')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'is_active', 'started_at', 'expires_at')
    list_filter = ('status', 'is_active', 'plan__plan_type')
    search_fields = ('user__phone_number', 'user__username')
    raw_id_fields = ('user',)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('user__phone_number', 'description')
    raw_id_fields = ('user', 'order')


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('authority', 'ref_id', 'user__phone_number')
    raw_id_fields = ('user',)
