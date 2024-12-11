from django_filters import rest_framework as filters

from accounts.models import Country

class CountryFilter(filters.FilterSet):
    country_name = filters.CharFilter(lookup_expr='icontains')
    currency_active = filters.BooleanFilter()

    class Meta:
        model = Country
        fields = ['country_name', 'currency_active']

