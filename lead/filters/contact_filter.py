import django_filters
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import Lead_Source
from ..models import Contact, Lead


class ContactFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_all_fields')
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all(), required=False)
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', required=False)
    is_archive = django_filters.BooleanFilter(field_name='is_archive', lookup_expr='exact', required=False)
    status = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact', required=False)
    lead_is_null = django_filters.BooleanFilter(field_name='lead', method='filter_lead_is_null', required=False)

    assigned_to = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name='lead__assigned_to', label="Assigned To Filter")
    lead_source = django_filters.ModelChoiceFilter(queryset=Lead_Source.objects.all(), label="Lead Source Filter")
    from_date = django_filters.DateFilter(field_name='created_on', lookup_expr='gte', label='From Date')
    to_date = django_filters.DateFilter(field_name='created_on', lookup_expr='lte', label='To Date', required=False)
    lead_status = django_filters.BaseInFilter(field_name='lead__lead_status__id', label="Lead Status Filter")
    created_by = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), label="Created By Filter")
    
    class Meta:
        model = Contact
        fields = ['name', 'lead', 'is_active', 'status', 'is_archive', 'lead_is_null', 'assigned_to', 'lead_source', 
                  'from_date', 'to_date', 'lead_status', 'created_by']
    
    def filter_lead_is_null(self, queryset, name, value):
        if value:
            return queryset.filter(lead__isnull=True)  
        return queryset
    
    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(company_name__icontains=value) |
            Q(phone_number__icontains=value)
        )
