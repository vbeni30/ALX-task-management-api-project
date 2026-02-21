"""
api/serializers.py
------------------
Handles conversion between Task model instances and JSON representation.

Includes validation logic for status and priority to ensure only valid choices
are accepted via the API.
"""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the Task model."""

    # Set user as read-only, as we set it automatically in the view
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 
            'priority', 'status', 'completed_at', 'user', 
            'created_at', 'updated_at'
        ]
        # completed_at is set by the system, not directly by user input via general update
        read_only_fields = ['completed_at', 'created_at', 'updated_at']

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
