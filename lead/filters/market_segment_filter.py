from rest_framework import viewsets
from django_filters import rest_framework as filters
from ..models import Market_Segment


class MarketSegmentFilter(filters.FilterSet):
    market_segment = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search
    is_active = filters.BooleanFilter()

    class Meta:
        model = Market_Segment
        fields = ['market_segment', 'is_active']
