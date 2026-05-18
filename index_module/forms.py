from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'sp-input',
                'placeholder': 'نام و نام خانوادگی',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'sp-input',
                'placeholder': 'example@email.com',
                'dir': 'ltr',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'sp-input',
                'placeholder': '09123456789',
                'dir': 'ltr',
            }),
            'subject': forms.Select(attrs={'class': 'sp-select'}),
            'message': forms.Textarea(attrs={
                'class': 'sp-input sp-textarea',
                'placeholder': 'پیام خود را بنویسید...',
                'rows': 5,
            }),
        }
        labels = {
            'name': 'نام و نام خانوادگی',
            'email': 'ایمیل',
            'phone': 'شماره موبایل (اختیاری)',
            'subject': 'موضوع',
            'message': 'متن پیام',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and (not phone.isdigit() or len(phone) != 11):
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.')
        return phone
