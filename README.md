# Task Management API — ALX BE Capstone

A production-ready RESTful Task Management API built with **Django 4.2** and **Django REST Framework**.

---

## Part 4 — What's New

| Feature | Details |
|---|---|
| **JWT Authentication** | Access + refresh tokens via `djangorestframework-simplejwt` |
| **Advanced Filtering** | Filter by `priority`, `status`, `due_date`, `category` |
| **Search** | Full-text search on `title` and `description` |
| **Ordering** | Client-controlled ordering on `due_date`, `priority`, `created_at` |
| **Categories** | New `Category` model (user-scoped) with full CRUD |
| **Pagination** | `PageNumberPagination`, default page size 5 (override with `?page_size=`) |
| **ModelViewSet** | All views refactored to `ModelViewSet` using `DefaultRouter` |

---

## Tech Stack

- Python 3.10+
- Django 4.2
- Django REST Framework 3.14+
- `djangorestframework-simplejwt` 5.x
- `django-filter` 23.x

---

## Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd task-management-api

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
py manage.py migrate

# Create a superuser (for admin access)
py manage.py createsuperuser

# Run the development server
py manage.py runserver
```

---

## Authentication

All API endpoints require a valid JWT **Bearer token**.

### Obtain tokens

```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**

```json
{
  "access":  "<short-lived access token>",
  "refresh": "<long-lived refresh token>"
}
```

### Refresh access token

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh token>"
}
```

**Use the token in every request:**

```http
Authorization: Bearer <access token>
```

---

## API Endpoints

### Tasks

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/tasks/` | List authenticated user's tasks |
| `POST` | `/api/tasks/` | Create a new task |
| `GET` | `/api/tasks/<id>/` | Retrieve a task |
| `PUT` | `/api/tasks/<id>/` | Full update a task |
| `PATCH` | `/api/tasks/<id>/` | Partial update a task |
| `DELETE` | `/api/tasks/<id>/` | Delete a task |
| `PATCH` | `/api/tasks/<id>/toggle/` | Toggle completion status |

### Categories

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/categories/` | List authenticated user's categories |
| `POST` | `/api/categories/` | Create a new category |
| `GET` | `/api/categories/<id>/` | Retrieve a category |
| `PUT` | `/api/categories/<id>/` | Full update a category |
| `PATCH` | `/api/categories/<id>/` | Partial update a category |
| `DELETE` | `/api/categories/<id>/` | Delete a category |

### Auth

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/token/` | Obtain access + refresh tokens |
| `POST` | `/api/token/refresh/` | Refresh access token |

---

## Filtering, Search & Ordering

All query parameters can be combined freely.

### Filter by field (exact match)

```
GET /api/tasks/?priority=HIGH
GET /api/tasks/?status=PENDING
GET /api/tasks/?due_date=2025-12-31
GET /api/tasks/?category=3
```

### Full-text search

```
GET /api/tasks/?search=meeting
```

Searches across `title` and `description`.

### Ordering

```
GET /api/tasks/?ordering=-due_date        # newest due date first
GET /api/tasks/?ordering=priority         # A-Z by priority
GET /api/tasks/?ordering=created_at       # oldest first
```

Prefix with `-` for descending order.

### Pagination

```
GET /api/tasks/?page=2
GET /api/tasks/?page=1&page_size=10
```

Default page size is **5**. Maximum page size is not capped — adjust in settings if needed.

---

## Task Model

| Field | Type | Notes |
|-------|------|-------|
| `title` | `CharField` | Required |
| `description` | `TextField` | Optional, defaults to `""` |
| `due_date` | `DateField` | Required |
| `priority` | `CharField` | `LOW` / `MEDIUM` / `HIGH` (default: `MEDIUM`) |
| `status` | `CharField` | `PENDING` / `COMPLETED` (default: `PENDING`) |
| `completed_at` | `DateTimeField` | Set automatically on completion |
| `category` | `ForeignKey` | Optional, must be user's own category |
| `user` | `ForeignKey` | Set automatically from JWT identity |
| `created_at` | `DateTimeField` | Auto-set on creation |
| `updated_at` | `DateTimeField` | Auto-set on every save |

---

## Category Model

| Field | Type | Notes |
|-------|------|-------|
| `name` | `CharField` | Unique per user (case-insensitive) |
| `user` | `ForeignKey` | Set automatically from JWT identity |
| `created_at` | `DateTimeField` | Auto-set on creation |

---

## Settings Overview

```python
# JWT tokens
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

# DRF global defaults
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # admin
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}
```

---

## Project Structure

```
task-management-api/
├── api/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── models.py       # Category + Task models
│   ├── serializers.py  # CategorySerializer + TaskSerializer
│   ├── views.py        # CategoryViewSet + TaskViewSet
│   └── urls.py         # DefaultRouter registration
├── taskmanager/
│   ├── settings.py     # JWT, filters, pagination config
│   └── urls.py         # Root URLs (token + api/ include)
├── manage.py
└── requirements.txt
```

---

## License

MIT
