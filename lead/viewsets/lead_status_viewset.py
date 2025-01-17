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