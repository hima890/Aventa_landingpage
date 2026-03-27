from rest_framework import serializers
from .models import PageView


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ['id', 'page', 'referrer', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']
