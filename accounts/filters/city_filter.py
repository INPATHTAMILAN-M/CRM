from django_filters import rest_framework as filters
from ..models import City

class CityFilter(filters.FilterSet):

    class Meta:
        model = City
        fields = ['state','city_name']


