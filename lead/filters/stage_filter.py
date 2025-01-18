from django_filters import rest_framework as filters

from accounts.models import Stage

class StageFilter(filters.FilterSet):
    is_active = filters.BooleanFilter()

    class Meta:
        model = Stage
        fields = ['is_active']
