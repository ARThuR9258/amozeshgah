from django.contrib import admin
from django.utils.html import format_html

from quizbuilder_module.models import Category, ExamSession, Question, UserAnswer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'question_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='تعداد سوال')
    def question_count(self, obj):
        return obj.questions.count()


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'is_correct', 'answered_at')
    can_delete = False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text_preview',
        'category',
        'difficulty',
        'correct_answer',
        'is_active',
        'thumb',
    )
    list_filter = ('is_active', 'category', 'difficulty', 'correct_answer')
    search_fields = ('text', 'option_1', 'option_2', 'option_3', 'option_4')
    autocomplete_fields = ('category',)

    fieldsets = (
        ('سوال', {'fields': ('text', 'image', 'category', 'difficulty', 'is_active')}),
        ('گزینه‌ها', {
            'fields': (
                ('option_1', 'option_1_image'),
                ('option_2', 'option_2_image'),
                ('option_3', 'option_3_image'),
                ('option_4', 'option_4_image'),
                'correct_answer',
            ),
        }),
    )

    @admin.display(description='متن')
    def text_preview(self, obj):
        return obj.text[:60] + '…' if len(obj.text) > 60 else obj.text

    @admin.display(description='تصویر')
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'status',
        'percent',
        'correct_count',
        'wrong_count',
        'started_at',
        'finished_at',
    )
    list_filter = ('status', 'passed')
    search_fields = ('user__phone_number', 'user__username')
    readonly_fields = ('question_ids', 'started_at', 'expires_at')
    inlines = [UserAnswerInline]


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'selected_choice', 'is_correct', 'answered_at')
    list_filter = ('is_correct',)
