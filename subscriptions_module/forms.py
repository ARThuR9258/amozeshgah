from django import forms
from django.contrib.auth import get_user_model

from .models import PaymentOrder, SubscriptionPlan, UserSubscription

User = get_user_model()


class SubscriptionPlanDashboardForm(forms.ModelForm):
    features_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'هر خط یک امکان (مثال: آزمون نامحدود)',
        }),
        label='امکانات (هر خط یک مورد)',
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            'slug', 'name', 'plan_type', 'description', 'price',
            'credits_amount', 'duration_days', 'daily_free_attempts',
            'is_popular', 'is_active', 'display_order',
        ]
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'credits_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_free_attempts': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.features:
            self.fields['features_text'].initial = '\n'.join(self.instance.features)

    def save(self, commit=True):
        instance = super().save(commit=False)
        text = self.cleaned_data.get('features_text', '')
        instance.features = [line.strip() for line in text.splitlines() if line.strip()]
        if commit:
            instance.save()
        return instance


class PaymentOrderDashboardForm(forms.ModelForm):
    class Meta:
        model = PaymentOrder
        fields = ['status', 'amount', 'authority', 'ref_id', 'paid_at']
        labels = {
            'status': 'وضعیت سفارش',
            'amount': 'مبلغ (تومان)',
            'authority': 'کد مرجع درگاه',
            'ref_id': 'شماره پیگیری',
            'paid_at': 'زمان پرداخت',
        }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'authority': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'ref_id': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'paid_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class UserSubscriptionDashboardForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'status', 'is_active', 'started_at', 'expires_at']
        labels = {
            'user': 'کاربر',
            'plan': 'پلن',
            'status': 'وضعیت',
            'is_active': 'فعال',
            'started_at': 'شروع',
            'expires_at': 'پایان',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'plan': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'started_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'expires_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all().order_by('-date_joined')[:500]
