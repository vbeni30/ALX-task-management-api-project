"""
api/urls.py
-----------
API route definitions — Part 4.

Uses DRF's DefaultRouter to auto-generate all standard CRUD URLs for
CategoryViewSet and TaskViewSet, plus the custom `toggle` action.

Generated routes (prefix = /api/):
  Categories:
    GET    /api/categories/           -> list
    POST   /api/categories/           -> create
    GET    /api/categories/<id>/      -> retrieve
    PUT    /api/categories/<id>/      -> update
    PATCH  /api/categories/<id>/      -> partial_update
    DELETE /api/categories/<id>/      -> destroy

  Tasks:
    GET    /api/tasks/                -> list
    POST   /api/tasks/                -> create
    GET    /api/tasks/<id>/           -> retrieve
    PUT    /api/tasks/<id>/           -> update
    PATCH  /api/tasks/<id>/           -> partial_update
    DELETE /api/tasks/<id>/           -> destroy
    PATCH  /api/tasks/<id>/toggle/    -> toggle (custom action)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, TaskViewSet, RegisterView

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
]
