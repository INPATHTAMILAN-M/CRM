from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from lead.custompagination import Paginator
from lead.filters.source_from_filter import LeadSourceFromFilter
from lead.serializers.source_from_serializer import LeadSourceFromSerializer
from ..models import Lead_Source_From


class LeadSourceFromViewSet(viewsets.ModelViewSet):
    queryset = Lead_Source_From.objects.all()
    serializer_class = LeadSourceFromSerializer
    filter_backends = (DjangoFilterBackend,)  
    filterset_class = LeadSourceFromFilter  
    pagination_class = Paginator