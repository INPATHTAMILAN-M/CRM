
import django_filters
from ..models import Log_Stage
from django_filters import rest_framework as filters


class LogStageFilter(django_filters.FilterSet):
    is_active = filters.BooleanFilter()
   
    class Meta:
        model = Log_Stage
        fields = ['is_active']
    