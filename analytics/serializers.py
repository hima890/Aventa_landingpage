from rest_framework import serializers

from .models import PageView

_MAX_USER_AGENT_LENGTH = 512


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ['id', 'page', 'referrer', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_page(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Page path must not be empty.')
        return value

    def validate_referrer(self, value):
        if value is None:
            return value
        return value.strip()

    def validate_user_agent(self, value):
        if value is None:
            return value
        return value.strip()[:_MAX_USER_AGENT_LENGTH]
