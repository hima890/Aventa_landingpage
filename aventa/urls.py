"""
URL configuration for aventa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

from analytics.views import DashboardStatsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/submissions/', include('submissions.urls')),
    path('api/page-views/', include('analytics.urls')),
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
