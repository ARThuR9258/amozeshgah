from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SampleQuestion

@admin.register(SampleQuestion)
class SampleQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_link', 'file_size', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('file_preview', 'file_size', 'created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'is_active')
        }),
        ('فایل سوالات', {
            'fields': ('pdf_file', 'file_preview', 'file_size')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_link(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">دانلود فایل</a>', 
                obj.pdf_file.url
            )
        return "-"
    file_link.short_description = 'لینک فایل'
    
    def file_preview(self, obj):
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">مشاهده فایل</a>',
                obj.pdf_file.url
            )
        return "فایلی آپلود نشده است"
    file_preview.short_description = 'پیش‌نمایش فایل'
    file_preview.allow_tags = True
    
    def file_size(self, obj):
        return obj.get_file_size()
    file_size.short_description = 'حجم فایل'
