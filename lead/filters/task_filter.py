from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from ..models import Task
import django_filters

class TaskFilter(filters.FilterSet):
    #created_on = filters.DateFromToRangeFilter()
    lead = filters.NumberFilter(field_name='contact__lead__id')   
    # assigned_to = filters.CharFilter(method='filter_assigned_to', label="Assigned To")
    # owner = filters.BaseInFilter()
    # task_date_time = filters.DateTimeFilter()
    # task_detail = filters.CharFilter(lookup_expr='icontains')
    # created_by = filters.BaseInFilter()
    # tasktype = filters.ChoiceFilter(choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')])
    # contact = filters.BaseInFilter()
    # log = filters.BaseInFilter()
    search = filters.CharFilter(method='filter_search', lookup_expr='icontains')
    from_date_to_date = django_filters.DateFromToRangeFilter(field_name='created_on', method='filter_from_date_to_date')

    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)
    
    # def filter_assigned_to(self, queryset, name, value):
    #     user_ids = value.split(",")
    #     return queryset.filter(task_assignment__assigned_to__id__in=user_ids)
    
    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead',
                 'task_date_time', 'task_detail', 'created_by', 'tasktype',
                 'contact', 'log', 'search']
        
    def filter_from_date_to_date(self, queryset, name, value):
        # Custom filter for 'from_date_to_date', automatically handled by Django's DateFromToRangeFilter
        if value:
            return queryset.filter(created_on__range=[value.start, value.stop])
        return queryset