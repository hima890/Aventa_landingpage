import re

from rest_framework import serializers

from .models import WaitlistSubmission

_PHONE_RE = re.compile(r'^\+?[\d\s\-\(\)]{7,30}$')


class WaitlistSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistSubmission
        fields = [
            'id',
            'full_name',
            'whatsapp',
            'business_name',
            'business_type',
            'main_problem',
            'notes',
            'submitted_at',
        ]
        read_only_fields = ['id', 'submitted_at']

    def validate_full_name(self, value):
        return value.strip()

    def validate_whatsapp(self, value):
        value = value.strip()
        if not _PHONE_RE.match(value):
            raise serializers.ValidationError(
                'Enter a valid WhatsApp number (digits, spaces, +, -, parentheses; 7–30 chars).'
            )
        return value

    def validate_business_name(self, value):
        return value.strip()

    def validate_business_type(self, value):
        return value.strip()

    def validate_main_problem(self, value):
        return value.strip()

    def validate_notes(self, value):
        if value is None:
            return value
        return value.strip()
