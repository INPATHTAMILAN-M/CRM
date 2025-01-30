import django_filters
from django.contrib.auth.models import User
from django.db.models import Q
from ..models import Contact, Lead


class ContactFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all(), required=False)
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact', required=False)
    is_archive = django_filters.BooleanFilter(field_name='is_archive', lookup_expr='exact', required=False)
    status = django_filters.NumberFilter(field_name='status__id', lookup_expr='exact', required=False)
    lead_is_null = django_filters.BooleanFilter(field_name='lead', method='filter_lead_is_null', required=False)

    assigned_to = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name='lead__assigned_to', label="Assigned To Filter")
    lead_source = django_filters.NumberFilter(field_name='lead__lead_source__id', label="Lead Source Filter")
    from_date = django_filters.DateFilter(field_name='lead__created_on', lookup_expr='gte', label='From Date')
    to_date = django_filters.DateFilter(field_name='lead__created_on', lookup_expr='lte', label='To Date', required=False)
    lead_status = django_filters.NumberFilter(field_name='lead__lead_status__id', label="Lead Status Filter")
    created_by = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name='lead__created_by', label="Created By Filter")
    bdm = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), method='filter_bdm', label="BDM Filter", required=False)
    bde = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_bde', label="BDE Filter", required=False)    
    
    class Meta:
        model = Contact
        fields = ['name', 'lead', 'is_active', 'status', 'is_archive', 'lead_is_null', 'assigned_to', 'lead_source', 'from_date', 'to_date', 'lead_status', 'created_by', 'bdm', 'bde']
    def filter_lead_is_null(self, queryset, name, value):
        if value:
            return queryset.filter(lead__isnull=True)  
        return queryset
    
    def filter_bdm(self, queryset, name, value):
        if value:  
            return queryset.filter(
                Q(lead__lead_owner__in=value) | Q(lead__created_by__in=value)
            )
        return queryset

    def filter_bde(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(lead__assigned_to=value) | Q(lead__created_by=value)
            )
        return queryset