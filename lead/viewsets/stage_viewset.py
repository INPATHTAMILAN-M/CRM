from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..custompagination import Paginator
from ..models import Stage
from ..serializers.stage_serializers import *


class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    pagination_class = Paginator
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StageCreateSerializer
        if self.action == 'list':
            return StageListSerializer
        if self.action in ['update', 'partial_update']:
            return StageUpdateSerializer
        return StageRetrieveSerializer    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )