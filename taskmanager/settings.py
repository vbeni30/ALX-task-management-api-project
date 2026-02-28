"""
taskmanager/settings.py
-----------------------
Core Django settings for the Task Management API.

Key configurations:
  - REST_FRAMEWORK: JWT authentication, global filter backends, pagination
  - SIMPLE_JWT: Token lifetimes, algorithm, header type
  - DATABASES: SQLite for development (swap to PostgreSQL for production)

Production checklist:
  - Set SECRET_KEY from an environment variable (never commit the real key).
  - Set DEBUG=False.
  - Restrict ALLOWED_HOSTS to your domain(s).
  - Switch DATABASE to PostgreSQL or another production-grade engine.
"""

from pathlib import Path
from datetime import timedelta

# ---------------------------------------------------------------------------
# Build paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# SECURITY — change SECRET_KEY and DEBUG before deploying!
# ---------------------------------------------------------------------------
SECRET_KEY = "django-insecure-change-me-before-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",               # Django REST Framework
    "rest_framework_simplejwt",     # JWT Authentication
    "django_filters",               # Advanced filtering

    # Local apps
    "api",                          # Our Task Management app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "taskmanager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "taskmanager.wsgi.application"


# ---------------------------------------------------------------------------
# Database — SQLite for development; swap to PostgreSQL for production
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Django REST Framework configuration
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Authentication: JWT is primary; SessionAuthentication kept for admin browsable API.
    # BasicAuthentication removed — JWT replaces it for API clients.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    # All endpoints require an authenticated user by default.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    # Filter backends applied globally — views can further restrict these.
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],

    # Pagination — 10 items per page by default.
    # Clients can override with ?page_size=N (capped at MAX_PAGE_SIZE=100).
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "PAGE_SIZE_QUERY_PARAM": "page_size",  # allow ?page_size=N
    "MAX_PAGE_SIZE": 100,                  # prevent abuse
}


# ---------------------------------------------------------------------------
# SimpleJWT configuration
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Access token expires after 60 minutes — short-lived for security.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    # Refresh token expires after 7 days — allows clients to stay logged in.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Issue a new refresh token on each refresh — invalidates the old one.
    # Enable BLACKLIST_AFTER_ROTATION (and add 'rest_framework_simplejwt.token_blacklist'
    # to INSTALLED_APPS) in production to fully revoke old refresh tokens.
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,

    # Algorithm used to sign tokens — HS256 is the standard default.
    "ALGORITHM": "HS256",

    # Header type sent with the token: "Bearer <token>"
    "AUTH_HEADER_TYPES": ("Bearer",),

    # JWT claim containing the user's primary key.
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
