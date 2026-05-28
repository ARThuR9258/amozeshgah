from django import forms

from quizbuilder_module.models import Category, Question


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'is_active', 'display_order')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            'text',
            'image',
            'option_1',
            'option_2',
            'option_3',
            'option_4',
            'option_1_image',
            'option_2_image',
            'option_3_image',
            'option_4_image',
            'correct_answer',
            'category',
            'difficulty',
            'is_active',
        )
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'option_1': forms.TextInput(attrs={'class': 'form-control'}),
            'option_2': forms.TextInput(attrs={'class': 'form-control'}),
            'option_3': forms.TextInput(attrs={'class': 'form-control'}),
            'option_4': forms.TextInput(attrs={'class': 'form-control'}),
            'option_1_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'option_2_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'option_3_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'option_4_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
