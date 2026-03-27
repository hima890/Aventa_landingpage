from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.permissions import IsAdminUser

User = get_user_model()


class LoginViewTests(APITestCase):
    """Tests for POST /api/auth/login/."""

    def setUp(self):
        self.url = reverse('auth-login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123',
        )

    def test_login_returns_token(self):
        response = self.client.post(
            self.url, {'email': 'test@example.com', 'password': 'securepassword123'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_creates_token_only_once(self):
        """Repeated logins must reuse the same token (get_or_create)."""
        self.client.post(self.url, {'email': 'test@example.com', 'password': 'securepassword123'})
        self.client.post(self.url, {'email': 'test@example.com', 'password': 'securepassword123'})
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)

    def test_login_wrong_password_rejected(self):
        response = self.client.post(
            self.url, {'email': 'test@example.com', 'password': 'wrongpassword'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_email_rejected(self):
        response = self.client.post(
            self.url, {'email': 'nobody@example.com', 'password': 'securepassword123'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_rejected(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.url, {'email': 'test@example.com', 'password': 'securepassword123'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields_rejected(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_email_format_rejected(self):
        response = self.client.post(
            self.url, {'email': 'not-an-email', 'password': 'securepassword123'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(APITestCase):
    """Tests for POST /api/auth/logout/."""

    def setUp(self):
        self.url = reverse('auth-logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepassword123',
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)

    def test_logout_deletes_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.client.post(self.url)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_logout_without_token_unauthorized(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class IsAdminUserPermissionTests(APITestCase):
    """Unit tests for the IsAdminUser permission class."""

    def _make_request(self, user):
        """Return a mock-style request object with the given user attached."""
        request = self.client.get('/').wsgi_request
        request.user = user
        return request

    def test_admin_user_has_permission(self):
        user = User.objects.create_user(
            username='admin', email='admin@example.com', password='pass', is_admin=True
        )
        permission = IsAdminUser()
        request = self._make_request(user)
        self.assertTrue(permission.has_permission(request, None))

    def test_non_admin_user_denied(self):
        user = User.objects.create_user(
            username='regular', email='regular@example.com', password='pass'
        )
        permission = IsAdminUser()
        request = self._make_request(user)
        self.assertFalse(permission.has_permission(request, None))
