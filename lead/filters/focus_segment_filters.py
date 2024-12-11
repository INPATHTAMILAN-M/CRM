from django_filters import rest_framework as filters
from ..models import Focus_Segment

class FocusSegmentFilter(filters.FilterSet):
    focus_segment = filters.CharFilter(lookup_expr='icontains')
    vertical = filters.NumberFilter(field_name='vertical__id')
    is_active = filters.BooleanFilter()

    class Meta:
        model = Focus_Segment
        fields = ['focus_segment', 'vertical', 'is_active']