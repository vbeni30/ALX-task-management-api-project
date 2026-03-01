from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Category

class Category(models.Model):
    """A user-defined label that can be applied to tasks."""

    # The user who owns this category.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    # Category names are unique per user (enforced at serializer level too).
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (owner: {self.user.username})"

    class Meta:
        ordering = ["name"]
        # A user cannot have two categories with the same name.
        unique_together = [("user", "name")]
        verbose_name_plural = "categories"


# Task

class Task(models.Model):
    """Represents a single task owned by a user."""

    # Priority choices
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    # Status choices
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"

    # Fields

    # The user who owns this task.
    # on_delete=CASCADE: if a user is deleted, their tasks are also deleted.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",           # lets us do user.tasks.all()
    )

    # Optional category — null/blank so old tasks remain valid.
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)

    # blank=True so description is optional when creating a task
    description = models.TextField(blank=True, default="")

    due_date = models.DateField()

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,       
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

    # Methods

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
