from rest_framework import viewsets
from ..models import TaskConversationLog
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.task_convo_filter import TaskConversationLogFilter
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
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

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskConversationLogCreateSerializer
        if self.action == 'list':
            return TaskConversationLogListSerializer
        if self.action in ['update', 'partial_update']:
            return TaskConversationLogUpdateSerializer
        return super().get_serializer_class()
    