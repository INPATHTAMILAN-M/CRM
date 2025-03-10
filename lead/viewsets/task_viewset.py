from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max, Q
from ..models import Task, Task_Assignment
from ..serializers.task_serializers import *
from ..custom_pagination import Paginator
from ..serializers.log_serializer import *
from ..filters.task_filter import TaskFilter
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    pagination_class = Paginator
    allowed_methods = ['GET', 'POST', 'PATCH', 'DELETE']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(is_active=True) if user.groups.filter(name='Admin').exists() else Task.objects.filter(
            Q(id__in=Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)) | Q(created_by=user)
        ).order_by('-task_date_time')

        if self.request.query_params.get('has_reply') is not None:
            queryset = queryset.annotate(latest_log=Max('task_conversation_logs__created_on')).order_by('-latest_log', '-id')
        
        return queryset.order_by('-task_date_time').distinct()
    
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
            'details':validated_data['remark'],
            'lead_log_status':validated_data['contact'].lead.lead_status if validated_data['contact'].lead else None,
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get('is_active',False)
        instance.is_active = is_active
        instance.save()

        if is_active == 'True':
            return Response(
                {"detail": "Activated Successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Deactivated Successfully."},
                status=status.HTTP_200_OK
            )
    
class CalanderTaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            queryset = Task.objects.filter(is_active=True)
        else:
            task_ids = Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)
            queryset = Task.objects.filter(Q(id__in=task_ids) | Q(created_by=user), is_active=True)

        return queryset.order_by('-task_date_time')

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer


