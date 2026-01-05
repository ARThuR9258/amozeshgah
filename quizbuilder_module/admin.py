from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Quiz)
admin.site.register(QuizQuestionChoice)
admin.site.register(QuizQuestion)
admin.site.register(UserQuiz)
admin.site.register(UserQuizQuestionAnswer)