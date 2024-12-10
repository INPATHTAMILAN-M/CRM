from django_filters import rest_framework as filters
from django.contrib.auth.models import User

# Define a filter for the users based on their group names
class UserFilter(filters.FilterSet):
    group = filters.CharFilter(field_name='groups__name', lookup_expr='in')

    class Meta:
        model = User
        fields = ['group']


