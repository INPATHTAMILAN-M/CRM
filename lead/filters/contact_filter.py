import django_filters
from ..models import Contact

class ContactFilter(django_filters.FilterSet):
    lead_id = django_filters.NumberFilter(field_name='lead__id', lookup_expr='exact')
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact')
    status = django_filters.CharFilter(field_name='status__name', lookup_expr='icontains')  # assuming status is a ForeignKey to a model

    class Meta:
        model = Contact
        fields = '__all__'
