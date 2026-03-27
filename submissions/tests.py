from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import WaitlistSubmission

User = get_user_model()

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    'full_name': 'Alice Smith',
    'whatsapp': '+1234567890',
    'business_name': 'Alice Corp',
    'business_type': 'Retail',
    'main_problem': 'Need more clients',
    'notes': '',
}


# ---------------------------------------------------------------------------
# POST /api/submissions/ (public)
# ---------------------------------------------------------------------------

class SubmissionCreateTests(APITestCase):
    """Tests for the public POST endpoint that records a waitlist submission."""

    def setUp(self):
        self.url = reverse('submission-list-create')

    def test_create_submission_success(self):
        response = self.client.post(self.url, VALID_PAYLOAD)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WaitlistSubmission.objects.count(), 1)

    def test_create_submission_returns_correct_fields(self):
        response = self.client.post(self.url, VALID_PAYLOAD)
        for field in ('id', 'full_name', 'whatsapp', 'business_name',
                      'business_type', 'main_problem', 'submitted_at'):
            self.assertIn(field, response.data)

    def test_create_submission_strips_whitespace_from_full_name(self):
        data = {**VALID_PAYLOAD, 'full_name': '  Alice Smith  '}
        self.client.post(self.url, data)
        self.assertEqual(WaitlistSubmission.objects.first().full_name, 'Alice Smith')

    def test_create_submission_strips_whitespace_from_business_name(self):
        data = {**VALID_PAYLOAD, 'business_name': '  Alice Corp  '}
        self.client.post(self.url, data)
        self.assertEqual(WaitlistSubmission.objects.first().business_name, 'Alice Corp')

    def test_create_submission_invalid_phone_rejected(self):
        data = {**VALID_PAYLOAD, 'whatsapp': 'not-a-phone'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_too_short_phone_rejected(self):
        data = {**VALID_PAYLOAD, 'whatsapp': '123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_valid_international_phone(self):
        data = {**VALID_PAYLOAD, 'whatsapp': '+44 (20) 7946-0958'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_submission_missing_full_name_rejected(self):
        data = {k: v for k, v in VALID_PAYLOAD.items() if k != 'full_name'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_missing_business_type_rejected(self):
        data = {k: v for k, v in VALID_PAYLOAD.items() if k != 'business_type'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_submission_notes_optional(self):
        data = {k: v for k, v in VALID_PAYLOAD.items() if k != 'notes'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submitted_at_is_read_only(self):
        """Clients cannot override the submission timestamp."""
        data = {**VALID_PAYLOAD, 'submitted_at': '2000-01-01T00:00:00Z'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['submitted_at'], '2000-01-01T00:00:00Z')


# ---------------------------------------------------------------------------
# GET /api/submissions/ (admin only)
# ---------------------------------------------------------------------------

class SubmissionListTests(APITestCase):
    """Tests for the admin-only GET endpoint that lists submissions."""

    def setUp(self):
        self.url = reverse('submission-list-create')
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com',
            password='adminpass', is_admin=True,
        )
        self.regular = User.objects.create_user(
            username='user', email='user@example.com', password='userpass',
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.regular_token = Token.objects.create(user=self.regular)
        WaitlistSubmission.objects.create(**{k: v for k, v in VALID_PAYLOAD.items()})

    def test_list_as_admin_succeeds(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_response_is_paginated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

    def test_list_returns_existing_submission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Alice Smith')

    def test_list_as_non_admin_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_unauthenticated_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
