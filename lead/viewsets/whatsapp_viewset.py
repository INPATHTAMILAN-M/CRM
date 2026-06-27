from rest_framework import viewsets
from django_filters import rest_framework as filters

from lead.models import Whatsapp
from lead.filters.whatsapp_filter import WhatsappFilter
from lead.serializers.whatsapp_serializer import WhatsappSerializer
from rest_framework.permissions import IsAuthenticated
from lead.custom_pagination import Paginator

class WhatsappViewSet(viewsets.ModelViewSet):
    queryset = Whatsapp.objects.all().order_by('-id')
    serializer_class = WhatsappSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = WhatsappFilter
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
