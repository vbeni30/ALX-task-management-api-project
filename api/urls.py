"""
api/urls.py
-----------
API route definitions.
"""

from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskToggleCompleteView

urlpatterns = [
    # General task listing and creation
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),

    # Individual task operations (GET, PUT, PATCH, DELETE)
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Dedicated endpoint for completing/uncompleting a task
    path('tasks/<int:pk>/toggle/', TaskToggleCompleteView.as_view(), name='task-toggle'),
]
