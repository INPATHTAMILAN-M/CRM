from rest_framework import viewsets
from django_filters import rest_framework as filters
from lead.custompagination import Paginator
from lead.filters.market_segment_filter import MarketSegmentFilter
from ..models import Market_Segment
from ..serializers.market_segment_serializer import MarketSegmentSerializer


class MarketSegmentViewSet(viewsets.ModelViewSet):
    queryset = Market_Segment.objects.all()
    serializer_class = MarketSegmentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MarketSegmentFilter
    pagination_class = Paginator
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )