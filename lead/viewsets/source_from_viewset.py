from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from lead.custompagination import Paginator
from lead.filters.source_from_filter import LeadSourceFromFilter
from lead.serializers.source_from_serializer import LeadSourceFromSerializer
from ..models import Lead_Source_From
from rest_framework import status
from rest_framework.response import Response

class LeadSourceFromViewSet(viewsets.ModelViewSet):
    queryset = Lead_Source_From.objects.all()
    serializer_class = LeadSourceFromSerializer
    filter_backends = (DjangoFilterBackend,)  
    filterset_class = LeadSourceFromFilter  
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