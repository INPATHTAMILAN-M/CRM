import django_filters
from django.contrib.auth.models import User
from django.db.models import Q
from ..models import Opportunity, Lead, Contact, Country


class OpportunityFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label="Search")
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())  # Filter by lead
    primary_contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all(), null_label="No Contact")  # Filter by primary contact
    name = django_filters.CharFilter(lookup_expr='icontains')  # Case-insensitive partial match
    owner = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by specific user
    opportunity_value = django_filters.RangeFilter()  # Allows filtering by range
    recurring_value_per_year = django_filters.RangeFilter()  # Allows filtering by range
    currency_type = django_filters.ModelChoiceFilter(queryset=Country.objects.all())  # Filter by currency type
    closing_date = django_filters.DateFromToRangeFilter()  # Date range filter
    probability_in_percentage = django_filters.RangeFilter()  # Filter by percentage range
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by user who created
    created_on = django_filters.DateFromToRangeFilter()  # Date range filter
    is_active = django_filters.BooleanFilter()  # Boolean filter
    
    class Meta:
        model = Opportunity
        fields = [
            'search',
            'lead',
            'primary_contact',
            'name',
            'owner',
            'opportunity_value',
            'recurring_value_per_year',
            'currency_type',
            'closing_date',
            'probability_in_percentage',
            'created_by',
            'created_on',
            'is_active',
        ]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(lead__first_name__icontains=value) |
            Q(lead__last_name__icontains=value) |
            Q(primary_contact__first_name__icontains=value) |
            Q(primary_contact__last_name__icontains=value) |
            Q(owner__first_name__icontains=value) |
            Q(owner__last_name__icontains=value)
        )