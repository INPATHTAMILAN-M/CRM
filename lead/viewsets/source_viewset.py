from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from lead.filters.source_filter import LeadSourceFilter
from lead.serializers.source_serializer import LeadSourceSerializer
from ..models import Lead_Source


# ModelViewSet for Lead_Source
class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = Lead_Source.objects.all()
    serializer_class = LeadSourceSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LeadSourceFilter 
