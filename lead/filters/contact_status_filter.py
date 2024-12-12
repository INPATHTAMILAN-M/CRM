from django_filters import rest_framework as django_filters

from accounts.models import Contact_Status

class ContactStatusFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Contact_Status
        fields = ['status', 'is_active']
