from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Task, Task_Assignment
from ..serializers.assignment_notification_serializer import TaskListSerializer

class AssignedNotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this API
    serializer_class = TaskListSerializer

    def get_queryset(self):
        # Get the logged-in user
        user = self.request.user

        # Calculate one day before the current time
        one_day_ago = timezone.now() - timedelta(days=1)

        # Filter tasks assigned to the logged-in user and where task_date_time is within one day before today
        return Task.objects.filter(
            task_task_assignments__assigned_to=user,  # Reverse relation to filter assigned tasks
            task_date_time__lte=one_day_ago,  # Task's task_date_time is on or before one day ago
            task_date_time__gte=one_day_ago - timedelta(days=1)  # Task's task_date_time is within the last day
        )
