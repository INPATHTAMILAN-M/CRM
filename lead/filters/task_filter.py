from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from ..models import Task


class TaskFilter(filters.FilterSet):
    created_on = filters.DateFromToRangeFilter()
    lead = filters.BaseInFilter(field_name='contact__lead__id')   
    assigned_to = filters.CharFilter(method='filter_assigned_to', label="Assigned To")
    owner = filters.BaseInFilter()
    task_date_time = filters.DateTimeFilter()
    task_detail = filters.CharFilter(lookup_expr='icontains')
    created_by = filters.BaseInFilter()
    tasktype = filters.ChoiceFilter(choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')])
    contact = filters.BaseInFilter()
    log = filters.BaseInFilter()
    search = filters.CharFilter(method='filter_search', lookup_expr='icontains')

    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)
    
    def filter_assigned_to(self, queryset, name, value):
        user_ids = value.split(",")
        return queryset.filter(task_assignment__assigned_to__id__in=user_ids)
    
    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead', 'owner', 
                 'task_date_time', 'task_detail', 'created_by', 'tasktype',
                 'contact', 'log', 'assigned_to', 'search']