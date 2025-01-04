import django_filters
from ..models import Contact, Lead


class ContactFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all(), required=False)
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', required=False)
    is_archive = django_filters.BooleanFilter(field_name='is_archive', lookup_expr='exact', required=False)
    status = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact', required=False)

    class Meta:
        model = Contact
        fields = ['name', 'lead', 'is_active', 'status','is_archive']