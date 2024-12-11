from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from lead.custompagination import Paginator
from ..models import Lead_Status
from ..serializers.lead_status_serializer import LeadStatusSerializer
from ..filters.lead_status_filter import LeadStatusFilter

class LeadStatusViewSet(viewsets.ModelViewSet):
    queryset = Lead_Status.objects.all()
    serializer_class = LeadStatusSerializer
    filter_backends = (DjangoFilterBackend,)  # Specify the filter backend
    filterset_class = LeadStatusFilter  # Use the filter class here
    pagination_class = Paginator