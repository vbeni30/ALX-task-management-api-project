"""
api/serializers.py
------------------
Serializers for the Task Management API — Part 4.

Serializers:
  - CategorySerializer: CRUD for user categories.
  - TaskSerializer:     Full task representation with optional category.

Validation highlights:
  - TaskSerializer.validate_category: ensures a user cannot assign another
    user's category to their own task.
  - Priority / Status validators kept from Part 3 for clean error messages.
"""

from rest_framework import serializers
from .models import Category, Task


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category — user is injected from request, not accepted
    from client input."""

    # Expose username for readability; never writable directly
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Category
        fields = ["id", "name", "user", "created_at"]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        """Category names must be unique per user (case-insensitive check)."""
        request = self.context.get("request")
        qs = Category.objects.filter(user=request.user, name__iexact=value)
        # On update, exclude the current instance from the uniqueness check
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You already have a category with this name."
            )
        return value


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task — user is injected from request, not accepted from
    client input. Category is optional and restricted to the request user's
    own categories."""

    # Expose the owning username as a read-only string
    user = serializers.ReadOnlyField(source="user.username")

    # Show the category name (read) alongside the writable category_id (write).
    # `category` returns the name; `category_id` is the FK integer field.
    category_name = serializers.CharField(
        source="category.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "priority",
            "status",
            "completed_at",
            "user",
            "category",         # writable FK id
            "category_name",    # read-only display name
            "created_at",
            "updated_at",
        ]
        # completed_at is managed by mark_complete / mark_incomplete helpers
        read_only_fields = ["completed_at", "created_at", "updated_at"]

    def validate_priority(self, value):
        """Ensure priority is one of the allowed choices (LOW, MEDIUM, HIGH)."""
        valid_choices = [choice[0] for choice in Task.Priority.choices]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid priority. Choose from: {', '.join(valid_choices)}"
            )
        return value

    def validate_status(self, value):
        """Ensure status is one of the allowed choices (PENDING, COMPLETED)."""
        valid_choices = [choice[0] for choice in Task.Status.choices]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Invalid status. Choose from: {', '.join(valid_choices)}"
            )
        return value

    def validate_category(self, value):
        """Prevent a user from assigning another user's category to their task."""
        if value is None:
            return value
        request = self.context.get("request")
        if value.user != request.user:
            raise serializers.ValidationError(
                "You can only assign your own categories to your tasks."
            )
        return value
