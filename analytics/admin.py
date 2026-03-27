from django.contrib import admin

from .models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'referrer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('page', 'referrer')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
