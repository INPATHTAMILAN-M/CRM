from django_filters import rest_framework as filters
from django_filters.filters import OrderingFilter
from accounts.models import State

class StateFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),  
        ),
        field_labels={
            'id': 'ID',
        }
    )
    state_name = filters.CharFilter(lookup_expr='icontains')
    country = filters.NumberFilter(field_name='country__id')  # Filter by country ID

    class Meta:
        model = State
        fields = ['state_name', 'country']
