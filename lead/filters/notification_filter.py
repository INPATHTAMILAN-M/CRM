import django_filters
from ..models import Notification
from django.db.models import Q

class NotificationFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type', lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_by_all_names', label='Search')

    class Meta:
        model = Notification
        fields = ['type', 'search']

    def filter_by_all_names(self, queryset, name, value):
        return queryset.filter(
            Q(lead__name__icontains=value) |
            Q(opportunity__lead__name__icontains=value) |
            Q(task__contact__lead__name__icontains=value) |
            Q(conversation__task__contact__lead__name__icontains=value)
        )
