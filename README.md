# Task Management API

A production-ready RESTful Task Management API built with **Django 4.2** and **Django REST Framework**.

Implements JWT authentication, user-scoped tasks and categories, advanced filtering, full-text search, client-controlled ordering, and pagination.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Filtering, Search & Ordering](#filtering-search--ordering)
- [Pagination](#pagination)
- [Data Models](#data-models)
- [Settings Overview](#settings-overview)
- [Running Tests](#running-tests)
- [cURL Examples](#curl-examples)

---

## Tech Stack

| Technology | Version |
|---|---|
| Python | 3.10+ |
| Django | 4.2.x |
| Django REST Framework | 3.14+ |
| djangorestframework-simplejwt | 5.x |
| django-filter | 23.x |

---

## Project Structure

```
task-management-api/
├── api/
│   ├── migrations/
│   ├── admin.py        # Enhanced admin for Category + Task
│   ├── models.py       # Category + Task models
│   ├── serializers.py  # CategorySerializer + TaskSerializer
│   ├── tests.py        # Unit + API integration tests
│   ├── views.py        # CategoryViewSet + TaskViewSet
│   └── urls.py         # DefaultRouter registration
├── taskmanager/
│   ├── settings.py     # JWT, filter backends, pagination config
│   └── urls.py         # Root URLs (token + api/ include)
├── manage.py
└── requirements.txt
```

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone (https://github.com/vbeni30/ALX-task-management-api-project.git)
cd task-management-api

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Create a superuser (optional — for admin access)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Authentication

All API endpoints require a valid JWT **Bearer token** in the `Authorization` header.

### 1. Obtain tokens

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
  "access":  "<short-lived access token — valid 60 min>",
  "refresh": "<long-lived refresh token — valid 7 days>"
}
```

### 2. Refresh the access token

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<refresh token>"
}
```

### 3. Use the token on every request

```http
Authorization: Bearer <access token>
```

---

## API Endpoints

### Tasks

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/tasks/` | List the authenticated user's tasks |
| `POST` | `/api/tasks/` | Create a new task |
| `GET` | `/api/tasks/<id>/` | Retrieve a specific task |
| `PUT` | `/api/tasks/<id>/` | Fully update a task |
| `PATCH` | `/api/tasks/<id>/` | Partially update a task |
| `DELETE` | `/api/tasks/<id>/` | Delete a task |
| `PATCH` | `/api/tasks/<id>/toggle/` | Toggle completion status |

### Categories

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/categories/` | List the authenticated user's categories |
| `POST` | `/api/categories/` | Create a new category |
| `GET` | `/api/categories/<id>/` | Retrieve a specific category |
| `PUT` | `/api/categories/<id>/` | Fully update a category |
| `PATCH` | `/api/categories/<id>/` | Partially update a category |
| `DELETE` | `/api/categories/<id>/` | Delete a category |

### Auth

| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/token/` | Obtain access + refresh tokens |
| `POST` | `/api/token/refresh/` | Refresh the access token |

---

## Filtering, Search & Ordering

All query parameters can be combined freely.

### Filter by exact field value

```
GET /api/tasks/?priority=HIGH
GET /api/tasks/?status=PENDING
GET /api/tasks/?due_date=2025-12-31
GET /api/tasks/?category=3
GET /api/tasks/?priority=HIGH&status=PENDING
```

### Full-text search

```
GET /api/tasks/?search=meeting
```

Searches across `title` and `description` (case-insensitive, partial match).

### Ordering

```
GET /api/tasks/?ordering=-due_date      # closest due date first
GET /api/tasks/?ordering=priority       # A–Z by priority
GET /api/tasks/?ordering=created_at     # oldest first
GET /api/tasks/?ordering=-created_at    # newest first (default)
```

Prefix with `-` for descending order.

### Category search & ordering

```
GET /api/categories/?search=work
GET /api/categories/?ordering=-created_at
```

---

## Pagination

Responses are paginated. Default page size is **10**. Clients can request up to **100** results per page.

```
GET /api/tasks/?page=2
GET /api/tasks/?page=1&page_size=20
GET /api/tasks/?page=1&page_size=100
```

**Paginated response shape:**

```json
{
  "count":    42,
  "next":     "http://127.0.0.1:8000/api/tasks/?page=2",
  "previous": null,
  "results":  [ ... ]
}
```

---

## Data Models

### Task

| Field | Type | Notes |
|-------|------|-------|
| `id` | `integer` | Auto-generated |
| `title` | `string` | Required, max 255 chars |
| `description` | `string` | Optional, defaults to `""` |
| `due_date` | `date` | Required (`YYYY-MM-DD`) |
| `priority` | `string` | `LOW` / `MEDIUM` / `HIGH` — default: `MEDIUM` |
| `status` | `string` | `PENDING` / `COMPLETED` — default: `PENDING` |
| `completed_at` | `datetime` | Set automatically on completion, `null` otherwise |
| `category` | `integer` | Optional FK — must be the user's own category |
| `category_name` | `string` | Read-only display label of the category |
| `user` | `string` | Read-only username of the owner |
| `created_at` | `datetime` | Auto-set on creation |
| `updated_at` | `datetime` | Auto-updated on every save |

### Category

| Field | Type | Notes |
|-------|------|-------|
| `id` | `integer` | Auto-generated |
| `name` | `string` | Required, unique per user (case-insensitive), max 100 chars |
| `user` | `string` | Read-only username of the owner |
| `created_at` | `datetime` | Auto-set on creation |

---

## Settings Overview

```python
# taskmanager/settings.py

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,   # new refresh token issued on every refresh call
    "ALGORITHM":              "HS256",
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # admin panel
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
    "PAGE_SIZE":              10,
    "PAGE_SIZE_QUERY_PARAM":  "page_size",
    "MAX_PAGE_SIZE":          100,
}
```

---

## Running Tests

```bash
python manage.py test api
```

The test suite covers:

- **Model unit tests** — `__str__`, `mark_complete`, `mark_incomplete`, default field values, and ordering.
- **Auth enforcement** — unauthenticated requests are rejected with `401 Unauthorized`.
- **User isolation** — users cannot read, modify, or delete another user's tasks or categories.
- **CRUD operations** — create, retrieve, and delete tasks and categories.
- **Toggle endpoint** — verifies `PENDING → COMPLETED → PENDING` transitions and `completed_at` handling.
- **Cross-user category assignment** — assigning another user's category to a task returns `400 Bad Request`.

---

## cURL Examples

> Replace `<ACCESS_TOKEN>` with the token returned by `POST /api/token/`.

### Obtain tokens

```bash
curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

### List your tasks

```bash
curl -s http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Create a task

```bash
curl -s -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Finish capstone project",
    "description": "Polish and submit the API project.",
    "due_date": "2025-12-31",
    "priority": "HIGH"
  }'
```

### Filter high-priority pending tasks

```bash
curl -s "http://127.0.0.1:8000/api/tasks/?priority=HIGH&status=PENDING" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Search tasks

```bash
curl -s "http://127.0.0.1:8000/api/tasks/?search=capstone" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Toggle a task's completion status

```bash
curl -s -X PATCH http://127.0.0.1:8000/api/tasks/1/toggle/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Create a category

```bash
curl -s -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work"}'
```

### Assign a category to a task (partial update)

```bash
curl -s -X PATCH http://127.0.0.1:8000/api/tasks/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"category": 2}'
```

### Refresh the access token

```bash
curl -s -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```

---

## Security Notes

- **User isolation is enforced at the queryset level**: `get_queryset()` always filters by `request.user` — there is no way for an authenticated user to access another user's resources.
- **Category ownership is validated at the serializer level**: `validate_category()` prevents cross-user category assignment.
- **`user` and `completed_at` are read-only**: clients cannot spoof ownership or manipulate completion timestamps directly.
- **JWT access tokens are short-lived (60 minutes)**: clients must refresh using the refresh token.
- **Rotate refresh tokens**: each refresh call issues a new refresh token, limiting token reuse windows.

---

## License

MIT
