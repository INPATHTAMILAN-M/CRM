from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Task, Task_Assignment
from ..serializers.task_serializers import *
from ..custompagination import Paginator
from ..serializers.log_serializer import *
from ..filters.task_filter import TaskFilter
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    pagination_class = Paginator
    alowed_methods = ['GET', 'POST', 'PATCH']
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return Task.objects.all()
        task_ids = Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)
        return Task.objects.filter(Q(id__in=task_ids) | Q(created_by=user))    
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action == 'list':
            return TaskListSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer
    
    
    def perform_create(self, serializer):
        # Check if 'task_date_time' is provided in the validated data
        task_date_time = serializer.validated_data.get('task_date_time', None)

        if not task_date_time:
            # If 'task_date_time' is missing, create a log instead of the task
            self.create_log_entry(serializer.validated_data)
            return  # Exit early, don't create a task

        # Proceed with the creation of the task if 'task_date_time' is provided
        serializer.save(created_by=self.request.user)

    def create_log_entry(self, validated_data):
        # Create a log entry instead of a task
        log_data = {
            'contact': validated_data['contact'],
            'lead': validated_data['contact'].lead if validated_data['contact'].lead else None,
            'log_stage': Log_Stage.objects.get(id=1),  # Assuming the log stage with id 1 exists
            'created_by': self.request.user,
        }

        # Assuming you have a Log model that accepts this information
        log = Log.objects.create(**log_data)
        return log

    def create(self, request, *args, **kwargs):
        # Validate data before creating
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Call perform_create to handle task creation or log creation
        self.perform_create(serializer)

        # Return a response based on whether the task was created or a log was created
        if serializer.validated_data.get('task_date_time'):
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Task date and time missing, a log was created instead."}, status=status.HTTP_200_OK)


class CalanderTaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    alowed_methods = ['GET']
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return Task.objects.all()
        task_ids = Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)
        return Task.objects.filter(Q(id__in=task_ids) | Q(created_by=user))
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer


