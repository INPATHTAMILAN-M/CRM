from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from..filters.task_assignment_filter import TaskAssignmentFilter
from ..models import Task_Assignment
from ..serializers.task_assignment_serializer import TaskAssignmentSerializer

class TaskAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Task_Assignment.objects.all()
    serializer_class = TaskAssignmentSerializer
    permission_classes = [IsAuthenticated]  
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskAssignmentFilter
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )