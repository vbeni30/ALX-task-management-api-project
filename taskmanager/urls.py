"""
taskmanager/urls.py
-------------------
Root URL configuration.

All task-related endpoints live under /api/ (versioned in the api app).
The Django admin is also mounted for convenience during development.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin (useful for inspecting data during development)
    path("admin/", admin.site.urls),

    # All API endpoints — prefixed with /api/
    # Actual route definitions live in api/urls.py
    path("api/", include("api.urls")),
]
