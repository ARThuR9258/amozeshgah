from django import forms
from account_module.models import User


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'نام کاربری' , 'class' : 'form-control'}),
        label='نام کاربری',
        error_messages={'required': 'نام کاربری الزامی است.'}
    )
    password = forms.CharField(
        min_length=8,
        max_length=200,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور' , 'class' : 'form-control'}),
        label='رمز عبور',
        error_messages={'required': 'رمز عبور الزامی است.', 'min_length': 'رمز عبور باید حداقل ۸ کاراکتر باشد.'}
    )
    password2 = forms.CharField(
        min_length=8,
        max_length=200,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور' , 'class': 'form-control'}),
        label='تکرار رمز عبور',
        error_messages={'required': 'تکرار رمز عبور الزامی است.', 'min_length': 'تکرار رمز عبور باید حداقل ۸ کاراکتر باشد.'}
    )

    class Meta:
        model = User
        # Bind only model fields; password fields are handled manually
        fields = ['email', 'username']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل', 'class': 'form-control'})
        }


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email = email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت‌نام شده است!')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('این نام کاربری قبلاً استفاده شده است!')
        return username

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('رمز عبور با تکرار آن مغایرت دارد!')
        return password2


    def save(self , commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'نام کاربری یا ایمیل',
            'class': 'form-control',
            'autocomplete': 'username'
        }),
        label='نام کاربری یا ایمیل',
        error_messages={'required': 'لطفاً نام کاربری یا ایمیل خود را وارد کنید.'}
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

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            from django.contrib.auth import authenticate
            user = authenticate(request=self.request, username=username, password=password)
            if user is None:
                raise forms.ValidationError('نام کاربری یا رمز عبور اشتباه است.')
            if not user.is_active:
                raise forms.ValidationError('حساب کاربری شما غیرفعال شده است.')
            cleaned_data['user'] = user
            
        return cleaned_data
