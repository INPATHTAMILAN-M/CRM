from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import rest_framework as filters
from django.utils import timezone

from ..models import Lead, Lead_Status
from accounts.models import Lead_Source
import django_filters

class LeadFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search', label="Search") 
    assigned_to = filters.ModelChoiceFilter(queryset=User.objects.all())
    lead_source = filters.ModelChoiceFilter(queryset=Lead_Source.objects.all())
    from_date = filters.DateFilter(field_name='created_on', lookup_expr='gte', label='From Date')
    to_date = filters.DateFilter(field_name='created_on', lookup_expr='lte', label='To Date', required=False)
    lead_status = filters.ModelChoiceFilter(queryset=Lead_Status.objects.all())
    created_by = filters.ModelChoiceFilter(queryset=User.objects.all())
    bdm = filters.BaseInFilter(method='filter_bdm', label="BDM Filter")
    bde = filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_bde', label="BDE Filter")
    user_id = django_filters.NumberFilter(method='filter_by_user_id', label="Filter by User ID (created_by or assigned_to)")
    def filter_to_date(self, queryset, name, value):
        """If no 'to_date' is provided, defaults to today."""
        if not value:
            value = timezone.now().date()  # Use today's date if no 'to_date' is provided
        return queryset.filter(created_on__lte=value)
    
    def filter_bdm(self, queryset, name, value):
        """
        Filter based on Business Development Manager (BDM).
        If a user ID is passed, it filters based on lead_owner and created_by.
        """
        # print("-----------------------------------------------", value)
        if value:  # If a BDM user ID is provided (value will be a list)
            return queryset.filter(
                Q(lead_owner__in=value) | Q(created_by__in=value)
            )
        return queryset

    def filter_bde(self, queryset, name, value):
        """
        Filter based on Business Development Executive (BDE).
        If a user ID is passed, it filters based on assigned_to and created_by.
        """
        if value:  # If a BDE user ID is provided
            return queryset.filter(
                Q(assigned_to=value) | Q(created_by=value)
            )
        return queryset
    
    class Meta:
        model = Lead
        fields = [
            'search',  
            'assigned_to',
            'lead_status',
            'lead_source',
            'bdm',
            'bde',
        ]

    def filter_search(self, queryset, name, value):
        """
        Custom method to handle the 'search' filter.
        Searches across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value)
           
        )
    def filter_by_user_id(self, queryset, name, value):
        """
        Filter opportunities by user_id where:
        - Match created_by user ID, OR
        - Match assigned_to user ID (via lead__assigned_to)
        """
        if value:
            return queryset.filter(
                Q(created_by__id=value) | Q(assigned_to__id=value)
            )
        return queryset