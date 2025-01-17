import django_filters
from accounts.models import Teams
from django.contrib.auth.models import User

class TeamsFilter(django_filters.FilterSet):
    bdm_user = django_filters.NumberFilter(field_name='bdm_user__id', lookup_expr='exact')

    class Meta:
        model = Teams
        fields = ['bdm_user']
