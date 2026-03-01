from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LoginView, RegisterView, DashboardView, TasksView, CategoriesView

urlpatterns = [

    # Django admin

    path("admin/", admin.site.urls),

 
    # JWT Auth API

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


    # REST API (tasks, categories, register)

    path("api/", include("api.urls")),


    # Frontend pages
    path("", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("tasks/", TasksView.as_view(), name="tasks"),
    path("categories/", CategoriesView.as_view(), name="categories"),
]
