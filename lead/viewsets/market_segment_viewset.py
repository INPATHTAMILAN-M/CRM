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