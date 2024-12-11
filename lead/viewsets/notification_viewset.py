
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from lead.models import Notification
from ..serializers.notification_serializers import *

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        if self.action == 'list':
            return NotificationListSerializer
        if self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
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
