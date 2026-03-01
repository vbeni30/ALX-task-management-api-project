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
