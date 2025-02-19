from rest_framework import viewsets
from ..models import TaskConversationLog
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.task_convo_filter import TaskConversationLogFilter
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.response import Response
from ..serializers.task_conversation_log_serializer import (
    TaskConversationLogCreateSerializer,
    TaskConversationLogUpdateSerializer,
    TaskConversationLogRetrieveSerializer,
    TaskConversationLogListSerializer,
)


class TaskConversationLogViewSet(viewsets.ModelViewSet):
    queryset = TaskConversationLog.objects.all()
    serializer_class = TaskConversationLogListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskConversationLogFilter
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        """Optimize queryset and filter by assigned_to or assigned_by"""
        user = self.request.user
        
        return TaskConversationLog.objects.filter(
            Q(task__task_task_assignments__assigned_to=user) |
            Q(task__task_task_assignments__assigned_by=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskConversationLogCreateSerializer
        if self.action == 'list':
            return TaskConversationLogListSerializer
        if self.action in ['update', 'partial_update']:
            return TaskConversationLogUpdateSerializer
        return super().get_serializer_class()
    
    def list(self, request, *args, **kwargs):
        """Override list to mark logs as viewed for the current user"""
        queryset = self.get_queryset()

        # Mark as viewed for the current user
        for log in queryset:
            log.mark_as_viewed(request.user)

        # Serialize and return the response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)