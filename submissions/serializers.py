from rest_framework import serializers
from .models import WaitlistSubmission


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
