from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.filters.teams_filter import TeamsFilter
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
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user', 'month', 'year', 'status']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserTargetCreateSerializer
        elif self.action == 'retrieve':
            return UserTargetRetrieveSerializer
        elif self.action == 'update':
            return UserTargetUpdateSerializer
        return UserTargetListSerializer
