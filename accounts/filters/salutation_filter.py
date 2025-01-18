from django_filters import rest_framework as filters
from ..models import Salutation

class SalutationFilter(filters.FilterSet):

    class Meta:
        model = Salutation
        fields = ['salutation','is_active']


