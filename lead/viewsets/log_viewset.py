from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..custompagination import Paginator
from ..models import Log
from ..serializers.logserializer import GetLogSerializer, PostLogSerializer

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    pagination_class = Paginator
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostLogSerializer
        return GetLogSerializer
    

