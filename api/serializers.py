"""
api/serializers.py
------------------
Serializers for the Task Management API.

Serializers:
  - CategorySerializer: CRUD for user-owned categories.
  - TaskSerializer:     Full task representation with optional category.

Security notes:
  - `user` is always a read-only field derived from `request.user` in the
    viewset's `perform_create()`. Clients cannot spoof ownership.
  - `validate_category` enforces that a task can only be assigned a category
    that belongs to the requesting user — preventing cross-user data leakage.
  - `completed_at` is read-only and is only modified through the `toggle`
    action on the viewset, which delegates to model helpers.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Task


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category.

    The `user` field is read-only and is injected from `request.user` by the
    viewset — clients cannot set or override it.
    """

    # Expose the owning username as a readable string; never writable.
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Category
        fields = ["id", "name", "user", "created_at"]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        """
        Enforce per-user uniqueness of category names (case-insensitive).

        On update, excludes the current instance so that renaming a category
        to a name that differs only in case from its current name is allowed.
        """
        request = self.context.get("request")
        qs = Category.objects.filter(user=request.user, name__iexact=value)
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
    """
    Serializer for Task.

    Read/write design:
      - `user`          – read-only username string (injected by viewset).
      - `category`      – writable FK integer (client sends a category id).
      - `category_name` – read-only label derived from the related Category.
      - `completed_at`  – read-only; managed by mark_complete/mark_incomplete.

    Validation:
      - `validate_category` ensures the supplied category belongs to the
        requesting user, preventing cross-user category assignment.
      - DRF automatically validates `priority` and `status` against their
        TextChoices, so no manual validator is needed for those fields.
    """

    # Owning username — never writable directly.
    user = serializers.ReadOnlyField(source="user.username")

    # Human-readable category label alongside the writable FK id.
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
            "category_name",    # read-only display label
            "created_at",
            "updated_at",
        ]
        # completed_at is managed exclusively by model helpers via the toggle action.
        read_only_fields = ["completed_at", "created_at", "updated_at"]

    def validate_category(self, value):
        """
        Prevent a user from assigning another user's category to their task.

        Raises ValidationError if the submitted category does not belong to
        the authenticated user making the request.
        """
        if value is None:
            return value
        request = self.context.get("request")
        if value.user != request.user:
            raise serializers.ValidationError(
                "You can only assign your own categories to your tasks."
            )
        return value


# ---------------------------------------------------------------------------
# User Registration
# ---------------------------------------------------------------------------

class UserRegisterSerializer(serializers.Serializer):
    """Serializer for new user registration (public endpoint)."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_username(self, value):
        """Ensure the username is not already taken."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
