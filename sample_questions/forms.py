from django import forms

from sample_questions.models import SampleQuestion

_WIDGET = {'class': 'form-control'}
_CHECK = {'class': 'form-check-input'}


class SampleQuestionDashboardForm(forms.ModelForm):
    class Meta:
        model = SampleQuestion
        fields = ['title', 'description', 'pdf_file', 'is_active']
        labels = {
            'title': 'عنوان',
            'description': 'توضیحات',
            'pdf_file': 'فایل PDF',
            'is_active': 'فعال',
        }
        widgets = {
            'title': forms.TextInput(attrs=_WIDGET),
            'description': forms.Textarea(attrs={**_WIDGET, 'rows': 3}),
            'pdf_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs=_CHECK),
        }
