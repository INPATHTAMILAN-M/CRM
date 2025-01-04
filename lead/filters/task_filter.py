from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from ..models import Task
import django_filters
from django.utils import timezone

class TaskFilter(filters.FilterSet):
    lead = filters.NumberFilter(field_name='contact__lead__id')   
    contact = filters.CharFilter(field_name='contact__name', lookup_expr='icontains', label='Contact Name') 
    
    
    # Add 'from_date' filter
    from_date = filters.DateFilter(field_name='task_date_time', lookup_expr='gte', label='From Date')
    
    # Add 'to_date' filter with custom logic
    to_date = filters.DateFilter(field_name='task_date_time', lookup_expr='lte', label='To Date', required=False)

    def filter_to_date(self, queryset, name, value):
        # If 'to_date' is not provided, default to today
        if not value:
            value = timezone.now().date()  # Use today's date
        return queryset.filter(task_date_time__lte=value)
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)

    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead',
                 'task_date_time', 'task_detail', 'created_by', 'tasktype',
                 'contact', 'log', ]
