from django.contrib import admin

from .models import WaitlistSubmission


@admin.register(WaitlistSubmission)
class WaitlistSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'business_name', 'business_type', 'whatsapp', 'submitted_at'
    )
    list_filter = ('business_type', 'submitted_at')
    search_fields = ('full_name', 'business_name', 'whatsapp')
    readonly_fields = ('submitted_at',)
    ordering = ('-submitted_at',)
