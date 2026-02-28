"""
api/views.py
------------
API ViewSets for the Task Management API — Part 4.

ViewSets:
  - CategoryViewSet: Full CRUD for user-owned categories.
  - TaskViewSet:     Full CRUD for tasks + a dedicated `toggle` action.

Key design decisions:
  - get_queryset() always filters by request.user — guarantees isolation.
  - perform_create() injects request.user automatically.
  - Filtering / search / ordering are declared per-viewset using DRF backends.
  - The toggle action replaces the old TaskToggleCompleteView while keeping
    identical business logic.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer, UserRegisterSerializer


# ---------------------------------------------------------------------------
# Category ViewSet
# ---------------------------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for the authenticated user's categories.

    list:   GET  /api/categories/
    create: POST /api/categories/
    read:   GET  /api/categories/<id>/
    update: PUT  /api/categories/<id>/
    partial_update: PATCH /api/categories/<id>/
    delete: DELETE /api/categories/<id>/
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    # Search and ordering — filtering not needed for categories
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Return only the categories belonging to the current user."""
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the category to the current user."""
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# Task ViewSet
# ---------------------------------------------------------------------------

class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for the authenticated user's tasks.

    list:   GET  /api/tasks/
    create: POST /api/tasks/
    read:   GET  /api/tasks/<id>/
    update: PUT  /api/tasks/<id>/
    partial_update: PATCH /api/tasks/<id>/
    delete: DELETE /api/tasks/<id>/
    toggle: PATCH /api/tasks/<id>/toggle/
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    # -----------------------------------------------------------------------
    # Filter / search / ordering backends
    # -----------------------------------------------------------------------
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Exact-match filters on these fields:
    #   /api/tasks/?priority=HIGH
    #   /api/tasks/?status=PENDING
    #   /api/tasks/?due_date=2025-12-31
    filterset_fields = ["priority", "status", "due_date", "category"]

    # Full-text search across title and description:
    #   /api/tasks/?search=meeting
    search_fields = ["title", "description"]

    # Client-controlled ordering:
    #   /api/tasks/?ordering=-due_date
    #   /api/tasks/?ordering=priority
    ordering_fields = ["due_date", "priority", "created_at"]
    ordering = ["-created_at"]      # default ordering (newest first)

    # -----------------------------------------------------------------------
    # Queryset — always scoped to request.user
    # -----------------------------------------------------------------------

    def get_queryset(self):
        """Return only the tasks belonging to the current user."""
        return Task.objects.filter(user=self.request.user).select_related("category")

    def perform_create(self, serializer):
        """Automatically assign the task to the current user."""
        serializer.save(user=self.request.user)

    # -----------------------------------------------------------------------
    # Custom action: toggle completion status
    # -----------------------------------------------------------------------

    @action(detail=True, methods=["patch"], url_path="toggle")
    def toggle(self, request, pk=None):
        """
        PATCH /api/tasks/<id>/toggle/

        Toggle a task between PENDING and COMPLETED.
        Optionally accept {"status": "COMPLETED"} or {"status": "PENDING"}
        in the request body to set an explicit state instead of toggling.
        """
        task = self.get_object()
        new_status = request.data.get("status")

        if new_status == Task.Status.COMPLETED:
            task.mark_complete()
        elif new_status == Task.Status.PENDING:
            task.mark_incomplete()
        else:
            # Simple toggle: flip current state
            if task.status == Task.Status.PENDING:
                task.mark_complete()
            else:
                task.mark_incomplete()

        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# User Registration (public)
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/

    Public endpoint — creates a new user account.
    Returns the new username on success (password is write-only).
    """

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Account created successfully.", "username": user.username},
            status=status.HTTP_201_CREATED,
        )
