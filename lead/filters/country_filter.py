from django_filters import rest_framework as filters
from django_filters.filters import OrderingFilter
from accounts.models import Country

class CountryFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),  
            ('country_name', 'country_name'),
        ),
        field_labels={
            'id': 'ID',
            'country_name': 'Country Name',
        }
    )
    country_name = filters.CharFilter(lookup_expr='icontains')
    currency_active = filters.BooleanFilter()

    class Meta:
        model = Country
        fields = ['country_name', 'currency_active']

