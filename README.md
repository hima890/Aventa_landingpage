# Aventa Landing Page — Backend API

A production-ready Django REST Framework API that powers the Aventa landing page.
It handles waitlist submissions, anonymous page-view analytics, and an admin
dashboard — all behind token-based authentication.

---

## Table of contents

- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Local setup](#local-setup)
- [Running tests](#running-tests)
- [API reference](#api-reference)
  - [Authentication](#authentication)
  - [Submissions](#submissions)
  - [Page views](#page-views)
  - [Dashboard](#dashboard)
- [Environment variables](#environment-variables)
- [Deployment notes](#deployment-notes)

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 6 + Django REST Framework 3 |
| Database | PostgreSQL (psycopg2-binary) |
| Auth | DRF Token Authentication |
| CORS | django-cors-headers |
| Config | python-dotenv |

---

## Project structure

```
aventa/            Django project (settings, root URL conf)
accounts/          Custom User model, login/logout endpoints, IsAdminUser permission
submissions/       WaitlistSubmission model + public create / admin list endpoints
analytics/         PageView model, page-view tracking, dashboard stats
```

---

## Local setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/hima890/Aventa_landingpage.git
cd Aventa_landingpage
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in every value (see [Environment variables](#environment-variables)).

### 4. Create the database and run migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py shell -c "
from accounts.models import User
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='changeme',
    is_admin=True,
)
"
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.

---

## Running tests

The test suite uses an in-memory SQLite database and does not require a running
PostgreSQL server or a `.env` file:

```bash
python manage.py test --settings=aventa.test_settings
```

All 46 tests should pass in under a second.

---

## API reference

All endpoints are prefixed with `/api/`.

### Authentication

#### `POST /api/auth/login/`

Public. Returns a token that must be sent as `Authorization: Token <key>` on
subsequent requests.

**Request body**

```json
{
  "email": "admin@example.com",
  "password": "changeme"
}
```

**Response `200 OK`**

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

**Error responses**

| Status | Reason |
|--------|--------|
| `400` | Wrong email, wrong password, or inactive account |

---

#### `POST /api/auth/logout/`

Requires a valid token. Deletes the token (forces re-login).

**Response `200 OK`**

```json
{ "detail": "Successfully logged out." }
```

**Error responses**

| Status | Reason |
|--------|--------|
| `401` | Missing or invalid token |

---

### Submissions

#### `POST /api/submissions/`

Public. Records a new waitlist submission. Rate-limited to **10 requests / hour**
per IP address.

**Request body**

```json
{
  "full_name": "Alice Smith",
  "whatsapp": "+1 (555) 123-4567",
  "business_name": "Alice Corp",
  "business_type": "Retail",
  "main_problem": "I need to reach more customers online.",
  "notes": "Optional extra context"
}
```

`notes` is optional. `whatsapp` accepts digits, spaces, `+`, `-`, and
parentheses (7–30 characters).

**Response `201 Created`**

```json
{
  "id": 1,
  "full_name": "Alice Smith",
  "whatsapp": "+1 (555) 123-4567",
  "business_name": "Alice Corp",
  "business_type": "Retail",
  "main_problem": "I need to reach more customers online.",
  "notes": "Optional extra context",
  "submitted_at": "2026-03-27T12:00:00Z"
}
```

**Error responses**

| Status | Reason |
|--------|--------|
| `400` | Missing required field or invalid phone number |
| `429` | Rate limit exceeded |

---

#### `GET /api/submissions/`

Admin only (`Authorization: Token <key>`, `is_admin=True`).
Returns a paginated list of all submissions (50 per page).

**Response `200 OK`**

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/submissions/?page=2",
  "previous": null,
  "results": [ { "id": 1, ... }, ... ]
}
```

**Error responses**

| Status | Reason |
|--------|--------|
| `401` | Missing or invalid token |
| `403` | Authenticated but not an admin |

---

### Page views

#### `POST /api/page-views/`

Public. Records a page visit for analytics. Rate-limited to **120 requests /
minute** per IP address.

**Request body**

```json
{
  "page": "/pricing",
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0 ..."
}
```

Only `page` is required. `user_agent` is truncated to 512 characters
server-side.

**Response `201 Created`**

```json
{
  "id": 7,
  "page": "/pricing",
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0 ...",
  "created_at": "2026-03-27T12:01:00Z"
}
```

**Error responses**

| Status | Reason |
|--------|--------|
| `400` | `page` is missing or blank |
| `429` | Rate limit exceeded |

---

### Dashboard

#### `GET /api/dashboard/stats/`

Admin only. Returns aggregated site statistics.

**Response `200 OK`**

```json
{
  "total_submissions": 120,
  "total_page_views": 3500,
  "daily_submissions": 8,
  "weekly_submissions": 47,
  "daily_page_views": 210,
  "weekly_page_views": 1400,
  "conversion_rate": 3.43,
  "business_type_breakdown": [
    { "business_type": "Retail", "count": 54 },
    { "business_type": "Tech", "count": 38 },
    { "business_type": "Services", "count": 28 }
  ]
}
```

`conversion_rate` is `(total_submissions / total_page_views) * 100`, rounded
to two decimal places. Returns `0.0` when there are no page views.

**Error responses**

| Status | Reason |
|--------|--------|
| `401` | Missing or invalid token |
| `403` | Authenticated but not an admin |

---

## Environment variables

Copy `.env.example` to `.env` and set the following:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Django secret key — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | ❌ | `True` for development, defaults to `False` |
| `ALLOWED_HOSTS` | ❌ | Comma-separated hosts, defaults to `localhost,127.0.0.1` |
| `DB_NAME` | ❌ | PostgreSQL database name, defaults to `aventa_db` |
| `DB_USER` | ❌ | PostgreSQL user, defaults to `aventa_user` |
| `DB_PASSWORD` | ✅ | PostgreSQL password |
| `DB_HOST` | ❌ | PostgreSQL host, defaults to `localhost` |
| `DB_PORT` | ❌ | PostgreSQL port, defaults to `5432` |
| `FRONTEND_URL` | ✅ in prod | Full origin of the Lovable frontend, e.g. `https://my-project.lovable.dev`. Required when `DEBUG=False`. |

---

## Deployment notes

When `DEBUG=False` the following security settings are automatically enabled:

- `SECURE_SSL_REDIRECT = True` — redirects all HTTP traffic to HTTPS
- `SECURE_HSTS_SECONDS = 31536000` with `includeSubDomains` and `preload`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'`

Ensure your hosting platform terminates TLS before the Django application and
forwards `X-Forwarded-Proto: https` so that `SECURE_SSL_REDIRECT` works
correctly.
