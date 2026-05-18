from django import forms

from quizbuilder_module.helpers import QUIZ_STATUS, UserQuizChoice
from quizbuilder_module.models import Quiz, QuizQuestion, QuizQuestionChoice, UserQuiz

_WIDGET = {'class': 'form-control'}
_SELECT = {'class': 'form-select'}
_CHECK = {'class': 'form-check-input'}


class QuizDashboardForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'desc', 'status', 'time', 'expire_time']
        labels = {
            'title': 'عنوان آزمون',
            'desc': 'توضیحات',
            'status': 'وضعیت',
            'time': 'مدت (دقیقه)',
            'expire_time': 'تاریخ پایان',
        }
        widgets = {
            'title': forms.TextInput(attrs=_WIDGET),
            'desc': forms.Textarea(attrs={**_WIDGET, 'rows': 3}),
            'status': forms.Select(attrs=_SELECT, choices=QUIZ_STATUS.CHOICES),
            'time': forms.NumberInput(attrs={**_WIDGET, 'min': 0}),
            'expire_time': forms.DateTimeInput(
                attrs={**_WIDGET, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }


class QuizQuestionChoiceDashboardForm(forms.ModelForm):
    class Meta:
        model = QuizQuestionChoice
        fields = ['text', 'image', 'is_answer']
        labels = {
            'text': 'متن گزینه',
            'image': 'تصویر (اختیاری)',
            'is_answer': 'پاسخ صحیح',
        }
        widgets = {
            'text': forms.TextInput(attrs=_WIDGET),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_answer': forms.CheckboxInput(attrs=_CHECK),
        }


class QuizQuestionDashboardForm(forms.ModelForm):
    choices = forms.ModelMultipleChoiceField(
        queryset=QuizQuestionChoice.objects.all().order_by('-id'),
        required=False,
        label='گزینه‌های سوال',
        help_text='چند گزینه را با Ctrl انتخاب کنید. ابتدا گزینه‌ها را در بخش «گزینه‌ها» بسازید.',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
    )

    class Meta:
        model = QuizQuestion
        fields = ['quiz', 'description', 'image', 'score', 'choices']
        labels = {
            'quiz': 'آزمون',
            'description': 'متن سوال',
            'image': 'تصویر سوال',
            'score': 'بارم',
        }
        widgets = {
            'quiz': forms.Select(attrs=_SELECT),
            'description': forms.Textarea(attrs={**_WIDGET, 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={**_WIDGET, 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quiz'].queryset = Quiz.objects.all().order_by('-id')
        if self.instance and self.instance.pk:
            self.fields['choices'].initial = self.instance.choices.all()


class UserQuizDashboardForm(forms.ModelForm):
    class Meta:
        model = UserQuiz
        fields = ['status', 'score']
        labels = {
            'status': 'وضعیت پاسخنامه',
            'score': 'نمره / بارم',
        }
        widgets = {
            'status': forms.Select(attrs=_SELECT, choices=UserQuizChoice.CHOICES),
            'score': forms.NumberInput(attrs={**_WIDGET, 'min': 0}),
        }
