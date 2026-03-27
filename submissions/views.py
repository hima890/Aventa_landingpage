from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from accounts.permissions import IsAdminUser
from .models import WaitlistSubmission
from .serializers import WaitlistSubmissionSerializer


class SubmissionListCreateView(APIView):
    """
    POST /api/submissions/ – public: create a new waitlist submission.
    GET  /api/submissions/ – admin only: list all submissions (paginated).
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        submissions = WaitlistSubmission.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(submissions, request, view=self)
        serializer = WaitlistSubmissionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = WaitlistSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
