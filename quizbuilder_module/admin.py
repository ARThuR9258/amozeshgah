from django.contrib import admin
from django.utils.html import format_html
from .models import *
# Register your models here.


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """پنل ادمین برای سوالات آزمون"""
    list_display = ['id', 'quiz', 'description_preview', 'image_thumbnail', 'score']
    list_filter = ['quiz', 'score']
    search_fields = ['description']
    
    def description_preview(self, obj):
        """نمایش خلاصه متن سوال در لیست"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'متن سوال'
    
    def image_thumbnail(self, obj):
        """نمایش تصویر بندانگشتی در لیست ادمین"""
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return 'بدون تصویر'
    image_thumbnail.short_description = 'تصویر'


admin.site.register(Quiz)
admin.site.register(QuizQuestionChoice)
admin.site.register(UserQuiz)
admin.site.register(UserQuizQuestionAnswer)