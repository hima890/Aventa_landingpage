from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permissions import IsAdminUser
from submissions.models import WaitlistSubmission
from .models import PageView
from .serializers import PageViewSerializer
from .throttles import PageViewRateThrottle


class PageViewCreateView(APIView):
    """POST /api/page-views/ – public: record a page view."""

    permission_classes = [AllowAny]

    def get_throttles(self):
        if self.request.method == 'POST':
            return [PageViewRateThrottle()]
        return super().get_throttles()

    def post(self, request):
        serializer = PageViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardStatsView(APIView):
    """GET /api/dashboard/stats/ – admin only: aggregated site statistics."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        total_submissions = WaitlistSubmission.objects.count()
        total_page_views = PageView.objects.count()

        daily_submissions = WaitlistSubmission.objects.filter(
            submitted_at__gte=day_ago
        ).count()
        weekly_submissions = WaitlistSubmission.objects.filter(
            submitted_at__gte=week_ago
        ).count()

        daily_page_views = PageView.objects.filter(created_at__gte=day_ago).count()
        weekly_page_views = PageView.objects.filter(created_at__gte=week_ago).count()

        conversion_rate = (
            round((total_submissions / total_page_views) * 100, 2)
            if total_page_views > 0
            else 0.0
        )

        business_type_breakdown = list(
            WaitlistSubmission.objects.values('business_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'total_submissions': total_submissions,
            'total_page_views': total_page_views,
            'daily_submissions': daily_submissions,
            'weekly_submissions': weekly_submissions,
            'daily_page_views': daily_page_views,
            'weekly_page_views': weekly_page_views,
            'conversion_rate': conversion_rate,
            'business_type_breakdown': business_type_breakdown,
        })
