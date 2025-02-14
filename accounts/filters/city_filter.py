from django_filters import rest_framework as filters
from ..models import City
from django_filters.filters import OrderingFilter

class CityFilter(filters.FilterSet):
    
    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),  # Allows sorting by 'id'
            ('city_name', 'city_name'),  # Sorting by 'city_name'
            ('state', 'state'),  # Sorting by 'state'
        ),
        field_labels={
            'id': 'ID',
            'city_name': 'City Name',
            'state': 'State',
        }
    )

    class Meta:
        model = City
        fields = ['state','city_name']


