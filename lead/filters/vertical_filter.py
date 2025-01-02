import django_filters
from accounts.models import Vertical

class VerticalFilter(django_filters.FilterSet):

    class Meta:
        model = Vertical
        fields = ['vertical', 'is_active']