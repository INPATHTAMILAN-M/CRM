from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..custompagination import Paginator
from ..models import Log
from ..serializers.log_serializer import GetLogSerializer, PostLogSerializer, PatchLogSerializer, ListLogSerializer
from ..filters import log_filter


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = log_filter.LogFilter
    pagination_class = Paginator
    alowed_methods = ['GET', 'POST', 'PATCH']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostLogSerializer
        if self.action == 'list':
            return ListLogSerializer
        if self.action in ['update', 'partial_update']:
            return PatchLogSerializer
        return GetLogSerializer    

