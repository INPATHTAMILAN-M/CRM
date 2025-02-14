from rest_framework import viewsets
from django_filters import rest_framework as filters
from lead.custom_pagination import Paginator
from lead.filters.market_segment_filter import MarketSegmentFilter
from ..models import Market_Segment
from ..serializers.market_segment_serializer import MarketSegmentSerializer
from rest_framework import status
from rest_framework.response import Response

class MarketSegmentViewSet(viewsets.ModelViewSet):
    queryset = Market_Segment.objects.all().order_by('-id')
    serializer_class = MarketSegmentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MarketSegmentFilter
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