"""
Test-only settings: uses SQLite in-memory DB and a dummy SECRET_KEY so that
`python manage.py test --settings=aventa.test_settings` works without a
running PostgreSQL server or a .env file.
"""

import os

# Provide dummy values before importing the main settings so that the startup
# guards in settings.py do not raise ValueError during the test run.
os.environ.setdefault('SECRET_KEY', 'test-secret-key-not-for-production')
os.environ.setdefault('FRONTEND_URL', 'http://localhost:3000')
# Activate DEBUG so that the production security hardening block in
# settings.py is skipped (SECURE_SSL_REDIRECT, HSTS, etc.) and the
# CORS FRONTEND_URL guard does not trigger.
os.environ.setdefault('DEBUG', 'True')

from aventa.settings import *  # noqa: F401,F403,E402

# Override database to use SQLite in-memory for fast, dependency-free tests.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Ensure security-redirect middleware does not interfere with the plain-HTTP
# requests made by the test client.
SECURE_SSL_REDIRECT = False

# Disable default throttle classes but keep custom scope rates so that
# per-view throttles (SubmissionRateThrottle, PageViewRateThrottle) can
# still resolve their scope without raising KeyError.  High limits ensure
# tests never hit the rate cap.
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []  # noqa: F405
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {  # noqa: F405
    'anon': '10000/hour',
    'submissions': '10000/hour',
    'page_views': '10000/minute',
}

# Speed up password hashing in tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
