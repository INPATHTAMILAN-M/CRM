from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import UserTarget
from ..serializers.user_target_serializer import (
    UserTargetCreateSerializer,
    UserTargetListSerializer,
    UserTargetRetrieveSerializer,
    UserTargetUpdateSerializer
)

class UserTargetViewSet(viewsets.ModelViewSet):
    queryset = UserTarget.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserTargetCreateSerializer
        elif self.action == 'retrieve':
            return UserTargetRetrieveSerializer
        elif self.action == 'update':
            return UserTargetUpdateSerializer
        return UserTargetListSerializer
