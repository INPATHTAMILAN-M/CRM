import django_filters
from django.contrib.auth.models import User
from django.db.models import Q
from ..models import Opportunity, Lead, Contact, Country, Lead_Source, Lead_Status, Opportunity_Status
from django.utils import timezone

class OpportunityFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label="Search")
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())  # Filter by lead
    primary_contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all(), null_label="No Contact")  # Filter by primary contact
    owner = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by specific user
    opportunity_value = django_filters.RangeFilter()  # Allows filtering by range
    recurring_value_per_year = django_filters.RangeFilter()  # Allows filtering by range
    currency_type = django_filters.ModelChoiceFilter(queryset=Country.objects.all())  # Filter by currency type
    closing_date = django_filters.DateFromToRangeFilter()  # Date range filter
    probability_in_percentage = django_filters.RangeFilter()  # Filter by percentage range
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by user who created
    created_on = django_filters.DateFromToRangeFilter()  # Date range filter
    is_active = django_filters.BooleanFilter()  # Boolean filter


    assigned_to = django_filters.ModelChoiceFilter(queryset=User.objects.all(), field_name='lead__assigned_to')
    lead_source = django_filters.ModelChoiceFilter(queryset=Lead_Source.objects.all(), field_name='lead__lead_source')
    from_date = django_filters.DateFilter(field_name='lead__created_on', lookup_expr='gte', label='From Date')
    to_date = django_filters.DateFilter(field_name='lead__created_on', lookup_expr='lte', label='To Date', required=False)
    lead_status = django_filters.ModelChoiceFilter(queryset=Lead_Status.objects.all(), field_name='lead__lead_status')
    opp_status = django_filters.CharFilter(field_name='opportunity_status__name', lookup_expr='exact')
    opportunity_status = django_filters.ModelChoiceFilter(queryset=Lead_Status.objects.all())
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all(), field_name='lead__created_by')    
    bdm = django_filters.BaseInFilter(method='filter_bdm', label="BDM Filter")
    bde = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_bde', label="BDE Filter")

    month = django_filters.BooleanFilter(method='filter_this_month', label="This Month")
    today = django_filters.BooleanFilter(method='filter_today', label="Today")


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
            'assigned_to',
            'assigned_to',
            'opp_status'
        ]


    def filter_to_date(self, queryset, name, value):
        if not value:
            value = timezone.now().date()  
        return queryset.filter(lead__created_on__lte=value)
    
    def filter_bdm(self, queryset, name, value):
        if value:  
            return queryset.filter(
                Q(lead__assigned_to__in=value) | Q(lead__created_by__in=value)
            )
        return queryset

    def filter_bde(self, queryset, name, value):
        if value:  
            return queryset.filter(
                Q(lead__assigned_to=value) | Q(lead__created_by=value)
            )
        return queryset    
    
    def filter_this_month(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(lead__created_on__month=timezone.now().month)|Q(status_date__month=timezone.now().month)
            )
        return queryset
    
    def filter_today(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(
                Q(lead__created_on__year=today.year,
                lead__created_on__month=today.month,
                lead__created_on__day=today.day)|Q(status_date=today)
            )
        return queryset    

    def search_filter(self, queryset, name, value):
        """Search by lead name or opportunity name."""
        return queryset.filter(
            Q(name__name__icontains=value) |  
            Q(lead__name__icontains=value)  
        )

    