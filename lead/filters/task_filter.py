from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from ..models import Task
import django_filters

class TaskFilter(filters.FilterSet):
    lead = filters.NumberFilter(field_name='contact__lead__id')   
    from_date_to_date = django_filters.DateFromToRangeFilter(field_name='created_on', method='filter_from_date_to_date')
    contact = filters.CharFilter(field_name='contact__name', lookup_expr='icontains', label='Contact Name') 
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)

    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead',
                 'task_date_time', 'task_detail', 'created_by', 'tasktype',
                 'contact', 'log', ]

    def filter_from_date_to_date(self, queryset, name, value):
        # Custom filter for 'from_date_to_date', automatically handled by Django's DateFromToRangeFilter
        if value:
            return queryset.filter(created_on__range=[value.start, value.stop])
        return queryset