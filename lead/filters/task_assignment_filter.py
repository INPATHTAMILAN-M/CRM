import django_filters
from ..models import Task_Assignment

class TaskAssignmentFilter(django_filters.FilterSet):
    assigned_to = django_filters.BaseInFilter(field_name='assigned_to__id', lookup_expr='exact')  # Filtering by `assigned_to`
    
    class Meta:
        model = Task_Assignment
        fields = ['assignment_note','assigned_on']  
