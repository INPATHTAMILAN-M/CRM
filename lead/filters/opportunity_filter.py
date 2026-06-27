import django_filters
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import Teams
from ..models import Opportunity, Lead, Contact, Country, Lead_Source, Lead_Status, Opportunity_Status
from django.utils import timezone

class OpportunityFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_on', 'created_on'),
        ),
        field_labels={
            'created_on': 'Created On',
        }
    )
    search = django_filters.CharFilter(method='search_filter', label="Search")
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())  # Filter by lead
    primary_contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all(), null_label="No Contact")  # Filter by primary contact
    owner = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by specific user
    opportunity_value = django_filters.RangeFilter()  # Allows filtering by range
    recurring_value_per_year = django_filters.RangeFilter()  # Allows filtering by range
    currency_type = django_filters.ModelChoiceFilter(queryset=Country.objects.all())  # Filter by currency type
    closing_date = django_filters.DateFromToRangeFilter()  # Date range filter
    probability_in_percentage = django_filters.RangeFilter()  # Filter by percentage range
    # created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())  # Filter by user who created
    created_on = django_filters.DateFromToRangeFilter()  # Date range filter
    is_active = django_filters.BooleanFilter()  # Boolean filter

    assigned_to = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_assigned_to')
    lead_source = django_filters.ModelChoiceFilter(queryset=Lead_Source.objects.all(), field_name='lead__lead_source')
    from_date = django_filters.DateFilter(method='filter_from_date', label='From Date')
    to_date = django_filters.DateFilter(method='filter_to_date', label='To Date', required=False)
    lead_status = django_filters.ModelChoiceFilter(queryset=Lead_Status.objects.all(), field_name='lead__lead_status')
    opp_status = django_filters.CharFilter(field_name='opportunity_status__name', lookup_expr='exact')
    opportunity_status = django_filters.ModelChoiceFilter(queryset=Lead_Status.objects.all())
    created_by = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_created_by')    
    bdm = django_filters.BaseInFilter(method='filter_bdm', label="BDM Filter")
    bde = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_bde', label="BDE Filter")
    assigned_leads = django_filters.BooleanFilter(method='filter_assigned_leads', label="Assigned Leads")
    role_asssigned = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_role_assigned', label="BDM Assigned")
    month = django_filters.BooleanFilter(method='filter_this_month', label="This Month")
    today = django_filters.BooleanFilter(method='filter_today', label="Today")
    team = django_filters.BooleanFilter(method='filter_team', label="Team Filter")
    user_id = django_filters.NumberFilter(method='filter_by_user_id', label="Filter by User ID (created_by or assigned_to)")


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
            'created_on',
            'is_active',
            'assigned_to',
            'opp_status'
        ]


    def filter_assigned_leads(self, queryset, name, value):
        if value:
            return queryset.filter(lead__assigned_to__isnull=False)
        return queryset
    
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
    
    def filter_role_assigned(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(lead__assigned_to=self.request.user) & Q(lead__created_by=value)
            )
        return queryset

    def filter_this_month(self, queryset, name, value):
        """Filter records created in the current month and year."""
        if value:
            return queryset.filter(
                Q(lead__created_on__month=timezone.now().month, lead__created_on__year=timezone.now().year) |
                Q(status_date__month=timezone.now().month, status_date__year=timezone.now().year)
            )
        return queryset

    def filter_today(self, queryset, name, value):
        """Filter records created today."""
        if value:
            today = timezone.now().date()
            return queryset.filter(
                Q(lead__created_on=today) | Q(status_date=today)
            )
        return queryset   

    def search_filter(self, queryset, name, value):
        """Search by lead name or opportunity name."""
        return queryset.filter(
            Q(name__name__icontains=value) |  
            Q(lead__name__icontains=value)  
        )
    
    def filter_team(self, queryset, name, value):
        """
        Filters queryset based on team relationships.
        Matches dashboard logic exactly:
        - Admin + team=true  → exclude lead__created_by=user OR lead__assigned_to=user
        - Admin + team=false → only lead__created_by=user OR lead__assigned_to=user
        - BDM + team=true    → team members' leads
        - BDM + team=false   → BDM's own leads
        - Others             → own leads only
        """
        request = self.request
        user = request.user

        is_admin = user.groups.filter(name__iexact="Admin").exists()
        is_bdm = user.groups.filter(name__iexact="BDM").exists()

        # --- Case 1: Admin ---
        if is_admin:
            if value:
                # team=true → exclude Admin's own created/assigned leads
                return queryset.exclude(
                    Q(lead__created_by=user) | Q(lead__assigned_to=user)
                )
            else:
                # team=false → only Admin's own
                return queryset.filter(
                    Q(lead__created_by=user) | Q(lead__assigned_to=user)
                )

        # --- Case 2: BDM ---
        if is_bdm:
            user_team = Teams.objects.filter(bdm_user=user).first()
            if not user_team:
                return queryset.none()

            if value:
                # team=true → show team members' opportunities
                team_member_ids = list(user_team.bde_user.values_list("id", flat=True))
                return queryset.filter(
                    Q(lead__assigned_to__in=team_member_ids) |
                    Q(lead__created_by__in=team_member_ids)
                )
            else:
                # team=false → show BDM's own
                return queryset.filter(
                    Q(lead__assigned_to=user) | Q(lead__created_by=user)
                )

        # --- Case 3: Regular user (BDE/TM etc.) ---
        return queryset.filter(
            Q(lead__assigned_to=user) | Q(lead__created_by=user)
        )
    
    def filter_by_user_id(self, queryset, name, value):
        """
        Filter opportunities by user_id where:
        - Match created_by user ID, OR
        - Match assigned_to user ID (via lead__assigned_to)
        """
        if value:
            return queryset.filter(
                Q(lead__created_by__id=value) | Q(lead__assigned_to__id=value)
            )
        return queryset

    def filter_from_date(self, queryset, name, value):
        """
        Filter opportunities by from_date, comparing against the most recent date 
        (updated_on if it exists and is greater, else created_on).
        """
        from django.db.models import Case, When, F
        if value:
            queryset = queryset.annotate(
                display_date=Case(
                    When(updated_on__isnull=False, updated_on__gt=F('created_on'), then=F('updated_on')),
                    default=F('created_on')
                )
            ).filter(display_date__gte=value)
        return queryset

    def filter_to_date(self, queryset, name, value):
        """
        Filter opportunities by to_date, comparing against the most recent date 
        (updated_on if it exists and is greater, else created_on).
        """
        from django.db.models import Case, When, F
        if value:
            queryset = queryset.annotate(
                display_date=Case(
                    When(updated_on__isnull=False, updated_on__gt=F('created_on'), then=F('updated_on')),
                    default=F('created_on')
                )
            ).filter(display_date__lte=value)
        return queryset

    def filter_created_by(self, queryset, name, value):
        if not value:
            return queryset
        
        assigned_to_id = self.request.query_params.get('assigned_to')
        if assigned_to_id:
            try:
                assigned_to_val = int(assigned_to_id)
                return queryset.filter(
                    Q(lead__created_by=value) | Q(lead__assigned_to_id=assigned_to_val)
                ).distinct()
            except ValueError:
                pass
        
        return queryset.filter(lead__created_by=value)

    def filter_assigned_to(self, queryset, name, value):
        if not value:
            return queryset
        
        created_by_id = self.request.query_params.get('created_by')
        if created_by_id:
            return queryset
            
        return queryset.filter(lead__assigned_to=value)
