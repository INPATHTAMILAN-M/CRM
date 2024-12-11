from django_filters import rest_framework as filters

from accounts.models import State

class StateFilter(filters.FilterSet):
    state_name = filters.CharFilter(lookup_expr='icontains')
    country = filters.NumberFilter(field_name='country__id')  # Filter by country ID

    class Meta:
        model = State
        fields = ['state_name', 'country']
