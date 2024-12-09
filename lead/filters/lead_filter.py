from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import rest_framework as filters

from ..models import Lead, Tag
from accounts.models import Country, State



class LeadFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search', label="Search")  # Custom search filter
    name = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive partial match
    lead_owner = filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by specific user
    created_by = filters.ModelChoiceFilter(queryset=User.objects.all())
    created_on = filters.DateFromToRangeFilter()  # Date range filter
    country = filters.ModelChoiceFilter(queryset=Country.objects.all())
    state = filters.ModelChoiceFilter(queryset=State.objects.all(), null_label='No State')  # Handles null states
    annual_revenue = filters.RangeFilter()  # Allows range filtering
    lead_type = filters.ChoiceFilter(choices=Lead.LEAD_TYPE_CHOICES)  # Dropdown for lead type
    is_active = filters.BooleanFilter()  # Boolean filter
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all())  # Filter by tags
    
    class Meta:
        model = Lead
        fields = [
            'search',  # Include the search field
            'name',
            'lead_owner',
            'created_by',
            'created_on',
            'country',
            'state',
            'annual_revenue',
            'lead_type',
            'is_active',
            'tags',
        ]

    def filter_search(self, queryset, name, value):
        """
        Custom method to handle the 'search' filter.
        Searches across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(company_email__icontains=value) |
            Q(company_website__icontains=value) |
            Q(fax__icontains=value)
        )

