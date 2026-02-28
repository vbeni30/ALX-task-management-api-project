"""
api/tests.py
------------
Basic test suite for the Task Management API.

Covers:
  - Unit tests for Category and Task model methods (__str__, mark_complete,
    mark_incomplete).
  - API integration tests for Task and Category endpoints:
      * Authentication enforcement (unauthenticated requests rejected).
      * User isolation (users cannot see each other's data).
      * Core CRUD operations and the toggle endpoint.

Run with:
    python manage.py test api
"""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Category, Task


# ===========================================================================
# Unit tests — model logic
# ===========================================================================

class CategoryModelTest(TestCase):
    """Unit tests for the Category model."""

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass1234")
        self.category = Category.objects.create(user=self.user, name="Work")

    def test_str_representation(self):
        """__str__ should include the category name and owner username."""
        self.assertIn("Work", str(self.category))
        self.assertIn("alice", str(self.category))

    def test_default_ordering_is_by_name(self):
        """Categories should be ordered alphabetically by name."""
        Category.objects.create(user=self.user, name="Zebra")
        Category.objects.create(user=self.user, name="Alpha")
        names = list(Category.objects.filter(user=self.user).values_list("name", flat=True))
        self.assertEqual(names, sorted(names))


class TaskModelTest(TestCase):
    """Unit tests for the Task model."""

    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="pass1234")
        self.task = Task.objects.create(
            user=self.user,
            title="Write tests",
            due_date=date.today(),
        )

    def test_str_representation(self):
        """__str__ should include priority and title."""
        result = str(self.task)
        self.assertIn("Write tests", result)
        self.assertIn(self.task.priority, result)

    def test_default_status_is_pending(self):
        """Newly created tasks should have PENDING status."""
        self.assertEqual(self.task.status, Task.Status.PENDING)

    def test_default_priority_is_medium(self):
        """Newly created tasks should default to MEDIUM priority."""
        self.assertEqual(self.task.priority, Task.Priority.MEDIUM)

    def test_mark_complete_sets_status_and_timestamp(self):
        """mark_complete() should set status to COMPLETED and record completed_at."""
        self.task.mark_complete()
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)
        self.assertIsNotNone(self.task.completed_at)

    def test_mark_incomplete_clears_status_and_timestamp(self):
        """mark_incomplete() should revert to PENDING and clear completed_at."""
        self.task.mark_complete()
        self.task.mark_incomplete()
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.PENDING)
        self.assertIsNone(self.task.completed_at)

    def test_completed_at_is_none_by_default(self):
        """completed_at should be None until the task is explicitly completed."""
        self.assertIsNone(self.task.completed_at)

    def test_default_ordering_is_newest_first(self):
        """Tasks should default to ordering by -created_at (newest first)."""
        t2 = Task.objects.create(user=self.user, title="Newer task", due_date=date.today())
        tasks = Task.objects.filter(user=self.user)
        self.assertEqual(tasks[0].pk, t2.pk)


# ===========================================================================
# API integration tests
# ===========================================================================

class AuthEnforcementTest(APITestCase):
    """Unauthenticated requests must be rejected with 401."""

    def test_tasks_requires_auth(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_categories_requires_auth(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskAPITest(APITestCase):
    """Integration tests for the Task endpoints."""

    def setUp(self):
        # Primary user
        self.user = User.objects.create_user(username="carol", password="pass1234")
        # Secondary user — should NOT be able to access carol's tasks
        self.other_user = User.objects.create_user(username="dave", password="pass1234")

        # Authenticate as the primary user via JWT
        response = self.client.post(
            "/api/token/",
            {"username": "carol", "password": "pass1234"},
            format="json",
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create a task owned by carol
        self.task = Task.objects.create(
            user=self.user,
            title="Carol's task",
            due_date=date.today(),
        )
        # Create a task owned by dave
        self.other_task = Task.objects.create(
            user=self.other_user,
            title="Dave's task",
            due_date=date.today(),
        )

    def test_list_returns_only_own_tasks(self):
        """GET /api/tasks/ should only return the authenticated user's tasks."""
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Carol's task", titles)
        self.assertNotIn("Dave's task", titles)

    def test_create_task(self):
        """POST /api/tasks/ should create a task owned by the requesting user."""
        payload = {
            "title": "New task",
            "due_date": str(date.today()),
            "priority": "HIGH",
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], "carol")

    def test_retrieve_own_task(self):
        """GET /api/tasks/<id>/ should return the task for its owner."""
        response = self.client.get(f"/api/tasks/{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Carol's task")

    def test_cannot_retrieve_other_users_task(self):
        """GET /api/tasks/<other_id>/ should return 404 for non-owner."""
        response = self.client.get(f"/api/tasks/{self.other_task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_toggle_pending_to_completed(self):
        """PATCH /api/tasks/<id>/toggle/ should mark a PENDING task as COMPLETED."""
        response = self.client.patch(f"/api/tasks/{self.task.pk}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "COMPLETED")
        self.assertIsNotNone(response.data["completed_at"])

    def test_toggle_completed_back_to_pending(self):
        """PATCH /api/tasks/<id>/toggle/ twice should return a task to PENDING."""
        self.client.patch(f"/api/tasks/{self.task.pk}/toggle/")
        response = self.client.patch(f"/api/tasks/{self.task.pk}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "PENDING")
        self.assertIsNone(response.data["completed_at"])

    def test_delete_task(self):
        """DELETE /api/tasks/<id>/ should remove the task."""
        response = self.client.delete(f"/api/tasks/{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


class CategoryAPITest(APITestCase):
    """Integration tests for the Category endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="eve", password="pass1234")
        self.other_user = User.objects.create_user(username="frank", password="pass1234")

        response = self.client.post(
            "/api/token/",
            {"username": "eve", "password": "pass1234"},
            format="json",
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.category = Category.objects.create(user=self.user, name="Personal")
        self.other_category = Category.objects.create(user=self.other_user, name="Private")

    def test_list_returns_only_own_categories(self):
        """GET /api/categories/ should only return the requesting user's categories."""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [c["name"] for c in response.data["results"]]
        self.assertIn("Personal", names)
        self.assertNotIn("Private", names)

    def test_create_category(self):
        """POST /api/categories/ should create a category owned by the requesting user."""
        response = self.client.post("/api/categories/", {"name": "Hobbies"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], "eve")

    def test_duplicate_category_name_rejected(self):
        """Creating a category with a duplicate name (case-insensitive) should fail."""
        response = self.client.post("/api/categories/", {"name": "personal"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_retrieve_other_users_category(self):
        """GET /api/categories/<other_id>/ should return 404 for non-owner."""
        response = self.client.get(f"/api/categories/{self.other_category.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_assign_other_users_category_to_task(self):
        """POST /api/tasks/ with another user's category id should return 400."""
        task_user = User.objects.create_user(username="eve_task", password="pass1234")
        # obtain token for eve (already logged in); try to assign frank's category
        payload = {
            "title": "Sneaky task",
            "due_date": str(date.today()),
            "category": self.other_category.pk,
        }
        response = self.client.post("/api/tasks/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
