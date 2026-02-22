"""
taskmanager/urls.py
-------------------
Root URL configuration — Part 4.

New in this part:
  - /api/token/         -> obtain JWT access + refresh token pair
  - /api/token/refresh/ -> exchange a refresh token for a new access token

All task and category endpoints remain under /api/.
The Django admin is still mounted for development convenience.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # -----------------------------------------------------------------------
    # Django admin — kept for direct data inspection during development
    # -----------------------------------------------------------------------
    path("admin/", admin.site.urls),

    # -----------------------------------------------------------------------
    # JWT Authentication endpoints
    # POST /api/token/          -> {"username": ..., "password": ...}
    #                              returns {"access": ..., "refresh": ...}
    # POST /api/token/refresh/  -> {"refresh": ...}
    #                              returns {"access": ...}
    # -----------------------------------------------------------------------
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # -----------------------------------------------------------------------
    # All API endpoints (tasks, categories) — routed through api/urls.py
    # -----------------------------------------------------------------------
    path("api/", include("api.urls")),
]
