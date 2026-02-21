"""
api/models.py
-------------
Defines the Task model — the core data entity for this API.

Design decisions:
  - Uses Django's built-in User model via ForeignKey so we don't need
    a custom user model in Part 3. This keeps things simple.
  - completed_at stores the exact moment a task was marked done.
    It is nullable because a PENDING task has no completion timestamp.
  - Choices are defined as class-level constants (TextChoices) so they
    are self-documenting and easy to extend later.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    """Represents a single task owned by a user."""

    # -----------------------------------------------------------------------
    # Priority choices
    # -----------------------------------------------------------------------
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    # -----------------------------------------------------------------------
    # Status choices
    # -----------------------------------------------------------------------
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"

    # -----------------------------------------------------------------------
    # Fields
    # -----------------------------------------------------------------------

    # The user who owns this task.
    # on_delete=CASCADE: if a user is deleted, their tasks are also deleted.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",           # lets us do user.tasks.all()
    )

    title = models.CharField(max_length=255)

    # blank=True so description is optional when creating a task
    description = models.TextField(blank=True, default="")

    due_date = models.DateField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,        # sensible default
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,         # every new task starts as pending
    )

    # Set only when a task is marked COMPLETED; null when PENDING
    completed_at = models.DateTimeField(null=True, blank=True)

    # Automatic timestamps for auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------------------------------------------------------
    # Methods
    # -----------------------------------------------------------------------

    def mark_complete(self):
        """Mark this task as COMPLETED and record the timestamp."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def mark_incomplete(self):
        """Revert a task to PENDING and clear the completion timestamp."""
        self.status = self.Status.PENDING
        self.completed_at = None
        self.save()

    def __str__(self):
        return f"[{self.priority}] {self.title} — {self.status}"

    class Meta:
        # Most recent tasks appear first by default
        ordering = ["-created_at"]
