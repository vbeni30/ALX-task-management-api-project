"""
api/admin.py
------------
Django admin configuration for the Task Management API.

Registers Category and Task with enhanced list views, filters,
and search capabilities so administrators can efficiently inspect
and manage data directly from the Django admin panel.
"""

from django.contrib import admin

from .models import Category, Task


# ---------------------------------------------------------------------------
# Category Admin
# ---------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin view for user-owned categories."""

    list_display = ["id", "name", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "user__username"]
    ordering = ["user__username", "name"]
    readonly_fields = ["created_at"]


# ---------------------------------------------------------------------------
# Task Admin
# ---------------------------------------------------------------------------

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin view for tasks with full filtering and search support."""

    list_display = [
        "id",
        "title",
        "user",
        "status",
        "priority",
        "due_date",
        "category",
        "created_at",
    ]
    list_filter = ["status", "priority", "due_date", "category"]
    search_fields = ["title", "description", "user__username"]
    ordering = ["-created_at"]
    readonly_fields = ["completed_at", "created_at", "updated_at"]

    # Group fields logically in the detail view
    fieldsets = [
        (
            "Task Info",
            {
                "fields": ["title", "description", "due_date"],
            },
        ),
        (
            "Classification",
            {
                "fields": ["priority", "status", "category"],
            },
        ),
        (
            "Ownership & Timestamps",
            {
                "fields": ["user", "completed_at", "created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]
