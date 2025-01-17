import django_filters
from ..models import Lead_Source

# Django Filter for Lead_Source
class LeadSourceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')  
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Lead_Source
        fields = ['name','is_active']  



