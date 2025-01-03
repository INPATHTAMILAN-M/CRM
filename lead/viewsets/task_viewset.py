from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Task, Task_Assignment
from ..serializers.task_serializers import *
from ..custompagination import Paginator
from ..serializers.log_serializer import *
from ..filters.task_filter import TaskFilter

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
        tasks = Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)
        return Task.objects.filter(id__in=tasks)    
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action == 'list':
            return TaskListSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer

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
        tasks = Task_Assignment.objects.filter(assigned_to=user,created_by=user).values_list("task", flat=True)
        return Task.objects.filter(id__in=tasks)    
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer


