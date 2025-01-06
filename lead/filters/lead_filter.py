import django_filters
import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import rest_framework as filters
from django.utils import timezone

from ..models import Lead, Lead_Status, Tag
from accounts.models import Country, Lead_Source, State



class LeadFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search', label="Search") 
    assigned_to = filters.ModelChoiceFilter(queryset=User.objects.all())
    lead_source = filters.ModelChoiceFilter(queryset=Lead_Source.objects.all())
     # Filtering by from_date and to_date for the created_on field
    from_date = filters.DateFilter(field_name='created_on', lookup_expr='gte', label='From Date')
    to_date = filters.DateFilter(field_name='created_on', lookup_expr='lte', label='To Date', required=False)
    lead_status = filters.ModelChoiceFilter(queryset=Lead_Status.objects.all())

    def filter_to_date(self, queryset, name, value):
        """If no 'to_date' is provided, defaults to today."""
        if not value:
            value = timezone.now().date()  # Use today's date if no 'to_date' is provided
        return queryset.filter(created_on__lte=value)
    
    class Meta:
        model = Lead
        fields = [
            'search',  
            'assigned_to',
            'lead_status',
            'lead_source',
        ]

    def filter_search(self, queryset, name, value):
        """
        Custom method to handle the 'search' filter.
        Searches across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(company_website__icontains=value) 
        )
   

    
    
    
    
 