"""
taskmanager/settings.py
-----------------------
Core Django settings for the Task Management API — Part 4.

CHANGES FROM PART 3:
  - Added 'rest_framework_simplejwt' and 'django_filters' to INSTALLED_APPS
  - Updated REST_FRAMEWORK config:
      * Authentication: JWTAuthentication (primary) + SessionAuthentication (admin)
      * Filter backends: DjangoFilterBackend, SearchFilter, OrderingFilter
      * Pagination: PageNumberPagination with page_size=5
  - Added SIMPLE_JWT config block with sensible token lifetimes
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
        "DIRS": [],
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

    # Pagination — 5 items per page by default; clients can override with ?page_size=N
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}


# ---------------------------------------------------------------------------
# SimpleJWT configuration
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Access token expires after 60 minutes — short-lived for security.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    # Refresh token expires after 7 days — allows clients to stay logged in.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Issue a new refresh token on each refresh call (sliding sessions).
    "ROTATE_REFRESH_TOKENS": False,

    # Blacklist old refresh tokens when rotated (requires simplejwt blacklist app).
    "BLACKLIST_AFTER_ROTATION": False,

    # Algorithm used to sign tokens — HS256 is the standard default.
    "ALGORITHM": "HS256",

    # Header type sent with the token: "Bearer <token>"
    "AUTH_HEADER_TYPES": ("Bearer",),
}
