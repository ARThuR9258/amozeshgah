from django import forms
from django.core.validators import MinLengthValidator
from account_module.models import User
from django.core.exceptions import ValidationError
import random


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'نام', 'class': 'form-control'}),
        label='نام',
        error_messages={'required': 'نام الزامی است.'}
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی', 'class': 'form-control'}),
        label='نام خانوادگی',
        error_messages={'required': 'نام خانوادگی الزامی است.'}
    )
    username = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'نام کاربری' , 'class': 'form-control'}),
        label='نام کاربری',
        error_messages={
            'required': 'نام کاربری الزامی است',
            'unique': 'این نام کاربری قبلا ثبت شده است'
        }
    )
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'شماره موبایل (09123456789)', 'class': 'form-control'}),
        label='شماره موبایل',
        error_messages={
            'required': 'شماره موبایل الزامی است.',
            'unique': 'این شماره موبایل قبلاً ثبت‌نام کرده است.'
        }
    )
    password = forms.CharField(
        min_length=8,
        max_length=200,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور', 'class': 'form-control'}),
        label='رمز عبور',
        error_messages={
            'required': 'رمز عبور الزامی است.',
            'min_length': 'رمز عبور باید حداقل ۸ کاراکتر باشد.'
        }
    )
    password2 = forms.CharField(
        min_length=8,
        max_length=200,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور', 'class': 'form-control'}),
        label='تکرار رمز عبور',
        error_messages={
            'required': 'تکرار رمز عبور الزامی است.',
            'min_length': 'تکرار رمز عبور باید حداقل ۸ کاراکتر باشد.'
        }
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number' , 'username']


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 11:
            raise forms.ValidationError('شماره موبایل معتبر نیست. لطفاً شماره موبایل را به درستی وارد کنید.')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('این شماره موبایل قبلاً ثبت‌نام کرده است!')
        return phone_number

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('رمز عبور با تکرار آن مغایرت دارد!')
        return password2


    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']
        user.set_password(self.cleaned_data['password'])
        
        # Generate a unique username if not provided
        if not user.username:
            base_username = f"user_{self.cleaned_data['phone_number']}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            user.username = username
            
        if commit:
            user.save()
        return user


class UserAddDashboardForm(forms.ModelForm):
    """Form for adding new users in the admin dashboard"""
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        }),
        min_length=8,
        required=True
    )
    confirm_password = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'تکرار رمز عبور'
        }),
        required=True
    )
    is_active = forms.BooleanField(
        label='فعال',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'switch-1'
        })
    )
    is_staff = forms.BooleanField(
        label='دسترسی ادمین',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'switch-2'
        })
    )
    is_verified = forms.BooleanField(
        label='تایید شده',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'switch-3'
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'phone_number', 'email',
            'is_active', 'is_staff', 'is_verified'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی',
                'required': 'required'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام کاربری',
                'required': 'required'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره موبایل (مثال: 09123456789)',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل (اختیاری)'
            }),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'username': 'نام کاربری',
            'phone_number': 'شماره موبایل',
            'email': 'ایمیل',
        }
        error_messages = {
            'phone_number': {
                'unique': 'این شماره موبایل قبلاً ثبت شده است.',
                'required': 'شماره موبایل الزامی است.'
            },
            'username': {
                'unique': 'این نام کاربری قبلاً ثبت شده است.',
                'required': 'نام کاربری الزامی است.'
            },
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 11:
            raise ValidationError('شماره موبایل باید 11 رقمی و فقط شامل اعداد باشد.')
        return phone_number

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('رمز عبور با تکرار آن مطابقت ندارد.')
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل (09123456789)',
            'class': 'form-control',
            'autocomplete': 'tel'
        }),
        label='شماره موبایل',
        error_messages={
            'required': 'لطفاً شماره موبایل خود را وارد کنید.',
            'invalid': 'شماره موبایل معتبر نیست.'
        }
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }),
        label='رمز عبور',
        error_messages={'required': 'لطفاً رمز عبور خود را وارد کنید.'}
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='مرا به خاطر بسپار',
        initial=True
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number or not phone_number.isdigit() or len(phone_number) != 11:
            raise forms.ValidationError('شماره موبایل معتبر نیست. لطفاً شماره موبایل ۱۱ رقمی را به درستی وارد کنید.')
        
        # Check if user exists with this phone number
        try:
            user = User.objects.get(phone_number=phone_number)
            self.user_cache = user
        except User.DoesNotExist:
            raise forms.ValidationError('کاربری با این شماره موبایل ثبت‌نام نکرده است.')
            
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')
        
        if phone_number and password:
            from django.contrib.auth import authenticate
            user = authenticate(request=self.request, username=phone_number, password=password)
            if user is None:
                raise forms.ValidationError('شماره موبایل یا رمز عبور اشتباه است.')
            if not user.is_active:
                raise forms.ValidationError('حساب کاربری شما غیرفعال شده است.')
            cleaned_data['user'] = user
            
        return cleaned_data

    def get_user(self):
        return self.user_cache if hasattr(self, 'user_cache') else None


class ForgotPasswordForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل (09123456789)',
            'class': 'form-control',
            'autocomplete': 'tel'
        }),
        label='شماره موبایل',
        error_messages={
            'required': 'لطفاً شماره موبایل خود را وارد کنید.',
            'invalid': 'شماره موبایل معتبر نیست.'
        }
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 11:
            raise forms.ValidationError('شماره موبایل معتبر نیست. لطفاً شماره موبایل را به درستی وارد کنید.')
        if not User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('کاربری با این شماره موبایل یافت نشد.')
        return phone_number


class ResetPasswordForm(forms.Form):
    code = forms.CharField(
        max_length=5,
        min_length=5,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'کد تایید',
            'class': 'form-control',
            'dir': 'ltr',
            'maxlength': '5'
        }),
        label='کد تایید',
        error_messages={
            'required': 'لطفاً کد تایید را وارد کنید.',
            'min_length': 'کد تایید باید ۵ رقمی باشد.',
            'max_length': 'کد تایید باید ۵ رقمی باشد.'
        }
    )
    
    new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'رمز عبور جدید',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }),
        label='رمز عبور جدید',
        validators=[MinLengthValidator(8)],
        error_messages={
            'required': 'لطفاً رمز عبور جدید را وارد کنید.',
            'min_length': 'رمز عبور باید حداقل ۸ کاراکتر باشد.'
        }
    )
    
    confirm_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'تکرار رمز عبور جدید',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }),
        label='تکرار رمز عبور جدید',
        error_messages={
            'required': 'لطفاً تکرار رمز عبور را وارد کنید.',
            'min_length': 'تکرار رمز عبور باید حداقل ۸ کاراکتر باشد.'
        }
    )
    
    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('رمز عبور با تکرار آن مطابقت ندارد.')
        return confirm_password