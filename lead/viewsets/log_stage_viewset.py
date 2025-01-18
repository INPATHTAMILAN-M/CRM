from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lead.filters.log_stage_filter import LogStageFilter

from ..custompagination import Paginator
from ..models import Log_Stage
from ..serializers.log_stageserializer import GetLogStageSerializer
from rest_framework import status
from rest_framework.response import Response

class LogStageViewSet(viewsets.ModelViewSet):
    queryset = Log_Stage.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogStageFilter
    pagination_class = Paginator
    serializer_class = GetLogStageSerializer
    alowed_methods = ['GET', 'POST']
    
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