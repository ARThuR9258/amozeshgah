from django import forms
from account_module.models import User


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
        fields = ['first_name', 'last_name', 'phone_number']


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