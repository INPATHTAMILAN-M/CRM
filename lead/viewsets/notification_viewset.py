
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from lead.custom_pagination import Paginator
from lead.filters.notification_filter import NotificationFilter
from lead.models import Notification
from ..serializers.notification_serializers import *
from django_filters.rest_framework import DjangoFilterBackend

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    filter_backends = [DjangoFilterBackend]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = Paginator
    filterset_class = NotificationFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationRetrieveSerializer  

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(receiver=self.request.user)

    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, receiver=request.user)
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
