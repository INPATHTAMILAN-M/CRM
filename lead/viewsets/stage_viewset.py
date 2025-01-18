from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lead.filters.stage_filter import StageFilter

from ..custompagination import Paginator
from ..models import Stage
from ..serializers.stage_serializers import *
from rest_framework import status
from rest_framework.response import Response

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = StageFilter
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
        is_active = request.data.get('is_active')
        instance.is_active = is_active
        instance.save()

        if is_active == 'True':
            return Response(
                {"detail": "Activated Successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Deactivated Successfully."},
                status=status.HTTP_200_OK
            )