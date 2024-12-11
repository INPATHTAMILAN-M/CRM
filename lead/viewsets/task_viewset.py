
from rest_framework import viewsets
from ..models import Task, Task_Assignment
from ..serializers.task_serializers import *

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name='admin').exists():
    #         return Task.objects.all()
    #     tasks = Task_Assignment.objects.filter(assigned_to=user).values_list("task", flat=True)
    #     return Task.objects.filter(id__in=tasks)    
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action == 'list':
            return TaskListSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer


