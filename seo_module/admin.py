from django.contrib import admin
from .models import GuidePage


@admin.register(GuidePage)
class GuidePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'display_order', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order', 'title')
