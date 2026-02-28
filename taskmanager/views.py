"""
taskmanager/views.py
--------------------
Minimal Django views that serve the frontend HTML templates.
All business logic lives in JavaScript that talks to /api/ endpoints.
"""

from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"


class RegisterView(TemplateView):
    template_name = "register.html"


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class TasksView(TemplateView):
    template_name = "tasks.html"


class CategoriesView(TemplateView):
    template_name = "categories.html"
