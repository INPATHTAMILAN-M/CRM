import django_filters
from ..models import Department

class DepartmentFilter(django_filters.FilterSet):
    # Filter by the 'department' field in Department
    department = django_filters.CharFilter(lookup_expr='icontains')  # 'icontains' allows case-insensitive partial matching
    is_active = django_filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = Department
        fields = ['department','is_active']  # You can add more fields if needed
