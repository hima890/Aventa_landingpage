from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from submissions.models import WaitlistSubmission
from .models import PageView

User = get_user_model()

# ---------------------------------------------------------------------------
# POST /api/page-views/ (public)
# ---------------------------------------------------------------------------

class PageViewCreateTests(APITestCase):
    """Tests for the public POST endpoint that records a page view."""

    def setUp(self):
        self.url = reverse('page-view-create')

    def test_create_page_view_success(self):
        response = self.client.post(self.url, {
            'page': '/home',
            'referrer': 'https://google.com',
            'user_agent': 'Mozilla/5.0',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PageView.objects.count(), 1)

    def test_create_page_view_minimal_payload(self):
        """Only `page` is required; referrer and user_agent are optional."""
        response = self.client.post(self.url, {'page': '/pricing'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_page_view_returns_correct_fields(self):
        response = self.client.post(self.url, {'page': '/home'})
        for field in ('id', 'page', 'referrer', 'user_agent', 'created_at'):
            self.assertIn(field, response.data)

    def test_create_page_view_empty_page_rejected(self):
        response = self.client.post(self.url, {'page': '   '})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_page_view_missing_page_rejected(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_page_value_is_stripped(self):
        self.client.post(self.url, {'page': '  /home  '})
        self.assertEqual(PageView.objects.first().page, '/home')

    def test_user_agent_truncated_to_512_chars(self):
        long_agent = 'A' * 600
        response = self.client.post(self.url, {'page': '/home', 'user_agent': long_agent})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(PageView.objects.first().user_agent), 512)

    def test_referrer_is_stripped(self):
        self.client.post(self.url, {'page': '/home', 'referrer': '  https://google.com  '})
        self.assertEqual(PageView.objects.first().referrer, 'https://google.com')

    def test_created_at_is_read_only(self):
        """Clients cannot override the creation timestamp."""
        response = self.client.post(
            self.url, {'page': '/home', 'created_at': '2000-01-01T00:00:00Z'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['created_at'], '2000-01-01T00:00:00Z')


# ---------------------------------------------------------------------------
# GET /api/dashboard/stats/ (admin only)
# ---------------------------------------------------------------------------

class DashboardStatsTests(APITestCase):
    """Tests for the admin-only dashboard statistics endpoint."""

    def setUp(self):
        self.url = reverse('dashboard-stats')
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='adminpass', is_admin=True,
        )
        self.regular = User.objects.create_user(
            username='user', email='user@example.com', password='userpass',
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.regular_token = Token.objects.create(user=self.regular)

    # --- access control ---

    def test_stats_as_admin_succeeds(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_as_non_admin_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stats_unauthenticated_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- response shape ---

    def test_stats_response_contains_all_expected_keys(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        expected_keys = [
            'total_submissions', 'total_page_views',
            'daily_submissions', 'weekly_submissions',
            'daily_page_views', 'weekly_page_views',
            'conversion_rate', 'business_type_breakdown',
        ]
        for key in expected_keys:
            self.assertIn(key, response.data)

    # --- aggregate counts ---

    def test_stats_reflect_correct_totals(self):
        PageView.objects.create(page='/home')
        PageView.objects.create(page='/pricing')
        WaitlistSubmission.objects.create(
            full_name='Bob', whatsapp='+1234567890',
            business_name='Bob Corp', business_type='Tech',
            main_problem='Growth',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['total_page_views'], 2)
        self.assertEqual(response.data['total_submissions'], 1)

    # --- conversion rate ---

    def test_conversion_rate_calculated_correctly(self):
        """50 % conversion: 1 submission out of 2 page views."""
        PageView.objects.create(page='/home')
        PageView.objects.create(page='/home')
        WaitlistSubmission.objects.create(
            full_name='Bob', whatsapp='+1234567890',
            business_name='Bob Corp', business_type='Tech',
            main_problem='Growth',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['conversion_rate'], 50.0)

    def test_conversion_rate_is_zero_when_no_page_views(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['conversion_rate'], 0.0)

    # --- business type breakdown ---

    def test_business_type_breakdown_is_sorted_by_count_descending(self):
        for _ in range(2):
            WaitlistSubmission.objects.create(
                full_name='Dev', whatsapp='+1000000000',
                business_name='Dev Corp', business_type='Tech',
                main_problem='Scale',
            )
        WaitlistSubmission.objects.create(
            full_name='Shop', whatsapp='+2000000000',
            business_name='Shop Co', business_type='Retail',
            main_problem='Revenue',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        breakdown = response.data['business_type_breakdown']
        self.assertEqual(len(breakdown), 2)
        self.assertEqual(breakdown[0]['business_type'], 'Tech')
        self.assertEqual(breakdown[0]['count'], 2)
        self.assertEqual(breakdown[1]['business_type'], 'Retail')
        self.assertEqual(breakdown[1]['count'], 1)

    def test_business_type_breakdown_empty_when_no_submissions(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['business_type_breakdown'], [])
