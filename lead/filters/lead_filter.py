import django_filters
import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters import rest_framework as filters
from django.utils import timezone

from ..models import Lead, Lead_Status, Tag
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
    lead_status = filters.ModelChoiceFilter(queryset=Lead_Status.objects.all(), null_label='No Lead Status')
    
    last_month = django_filters.BooleanFilter(method='filter_last_month', label="Last Month")
    this_month = django_filters.BooleanFilter(method='filter_this_month', label="This Month")
    last_7_days = django_filters.BooleanFilter(method='filter_last_7_days', label="Last 7 Days")
    from_date_to_date = django_filters.DateFromToRangeFilter(field_name='created_on', method='filter_from_date_to_date')

    
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
    def filter_last_month(self, queryset, name, value):
        # Calculate the first and last day of the previous month
        today = timezone.now().date()
        print("----------------today------------------",today)
        first_day_last_month = today.replace(day=1) - datetime.timedelta(days=1)
        print("-----------------first_day_last_month-----------------",first_day_last_month)
        first_day_last_month = first_day_last_month.replace(day=1)
        print("-----------------first_day_last_month-----------------",first_day_last_month)
        last_day_last_month = first_day_last_month.replace(day=28) + datetime.timedelta(days=4)  # Get the last day of the month
        print("----------------last_day_last_month------------------",last_day_last_month)
        last_day_last_month = last_day_last_month - datetime.timedelta(days=last_day_last_month.day)
        print("---------------last_day_last_month-------------------",last_day_last_month)
        # Filter leads created in the last month
        return queryset.filter(created_on__range=[first_day_last_month, last_day_last_month])

    def filter_this_month(self, queryset, name, value):
        # Get the first and last day of the current month
        today = timezone.now().date()
        first_day_this_month = today.replace(day=1)
        last_day_this_month = (first_day_this_month.replace(day=28) + datetime.timedelta(days=4)) - datetime.timedelta(days=(first_day_this_month.replace(day=28) + datetime.timedelta(days=4)).day)
        
        # Filter leads created in the current month
        return queryset.filter(created_on__range=[first_day_this_month, last_day_this_month])

    def filter_last_7_days(self, queryset, name, value):
        # Get the date 7 days ago from today
        today = timezone.now().date()
        last_7_days = today - datetime.timedelta(days=7)
        
        # Filter leads created in the last 7 days
        return queryset.filter(created_on__gte=last_7_days)
    
    def filter_from_date_to_date(self, queryset, name, value):
        # Custom filter for 'from_date_to_date', automatically handled by Django's DateFromToRangeFilter
        if value:
            return queryset.filter(created_on__range=[value.start, value.stop])
        return queryset