import django_filters
from ..models import Lead_Status
from django_filters import rest_framework as filters

class LeadStatusFilter(django_filters.FilterSet):
    # Filter by the 'name' field in Lead_Status
    name = django_filters.CharFilter(lookup_expr='icontains')  # 'icontains' allows case-insensitive partial matching
    is_active = filters.BooleanFilter()
    
    class Meta:
        model = Lead_Status
        fields = ['name','is_active']  # You can add more fields if needed
