import django_filters
from ..models import Lead_Source_From

class LeadSourceFromFilter(django_filters.FilterSet):
    # Filter by related LeadSource id (ForeignKey)
    lead_source_id = django_filters.NumberFilter(field_name='source__id')  # Filtering by LeadSource id
    # Filter by related LeadSource source (the name of the source)
    lead_source_name = django_filters.CharFilter(field_name='source__source', lookup_expr='icontains')  # Filtering by LeadSource source name
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Lead_Source_From
        fields = ['lead_source_id', 'lead_source_name','is_active']


