"""
api/views.py
------------
API Controller logic using Django REST Framework generic views.

Features:
  - TaskListCreateView: Lists current user's tasks and allows creating new ones.
  - TaskDetailView: Retrieve, Update, or Delete a specific task.
  - TaskToggleCompleteView: Dedicated endpoint to toggle completion status.

Permissions:
  - All views require 'IsAuthenticated'.
  - Users can only see and modify tasks where 'task.user == request.user'.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET: List all tasks for the authenticated user.
    POST: Create a new task for the authenticated user.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users must only see their own tasks
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the task to the current user
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific task.
    PUT/PATCH: Update a specific task.
    DELETE: Delete a specific task.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure the user can only access their own tasks
        return Task.objects.filter(user=self.request.user)


class TaskToggleCompleteView(generics.UpdateAPIView):
    """
    Endpoint to specifically mark a task as COMPLETED or PENDING.
    Implementation uses a custom action via PATCH/PUT.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        
        # Determine intended status from query param or toggle default
        # For simplicity in Part 3, we'll just toggle the state or 
        # look for a 'status' in the body.
        new_status = request.data.get('status')

        if new_status == Task.Status.COMPLETED:
            task.mark_complete()
        elif new_status == Task.Status.PENDING:
            task.mark_incomplete()
        else:
            # Simple toggle logic if no specific status provided
            if task.status == Task.Status.PENDING:
                task.mark_complete()
            else:
                task.mark_incomplete()

        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
