from django_filters import rest_framework as filters
from accounts.models import Tag


class TagFilter(filters.FilterSet):
    tag = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search
    is_active = filters.BooleanFilter()

    class Meta:
        model = Tag
        fields = ['tag', 'is_active']

