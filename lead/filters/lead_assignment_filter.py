import django_filters
from ..models import Lead_Assignment

class LeadAssignmentFilter(django_filters.FilterSet):
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id', lookup_expr='exact')  # Filtering by `assigned_to`
    
    class Meta:
        model = Lead_Assignment
        fields = ['assigned_to']  # Allow filtering by assigned_to (the user)
