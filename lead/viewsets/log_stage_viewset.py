from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..custompagination import Paginator
from ..models import Log_Stage
from ..serializers.log_stageserializer import GetLogStageSerializer
from ..filters import log_filter


class LogStageViewSet(viewsets.ModelViewSet):
    queryset = Log_Stage.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    # filterset_class = log_filter.LogFilter
    pagination_class = Paginator
    serializer_class = GetLogStageSerializer
    alowed_methods = ['GET', 'POST', 'PATCH']
    
    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return PostLogSerializer
    #     if self.action == 'list':
    #         return ListLogSerializer
    #     if self.action in ['update', 'partial_update']:
    #         return PatchLogSerializer
    #     return GetLogSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )