import django_filters
from ..models import Lead_Status

class LeadStatusFilter(django_filters.FilterSet):
    # Filter by the 'name' field in Lead_Status
    name = django_filters.CharFilter(lookup_expr='icontains')  # 'icontains' allows case-insensitive partial matching
    
    class Meta:
        model = Lead_Status
        fields = ['name']  # You can add more fields if needed
