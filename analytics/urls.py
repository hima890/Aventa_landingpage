from django.urls import path

from .views import PageViewCreateView

urlpatterns = [
    path('', PageViewCreateView.as_view(), name='page-view-create'),
]
