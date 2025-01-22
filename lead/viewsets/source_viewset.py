from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from lead.custompagination import Paginator
from lead.filters.source_filter import LeadSourceFilter
from lead.serializers.source_serializer import LeadSourceSerializer
from ..models import Lead_Source
from rest_framework import status
from rest_framework.response import Response

# ModelViewSet for Lead_Source
class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = Lead_Source.objects.all().order_by('-id')
    serializer_class = LeadSourceSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LeadSourceFilter 
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