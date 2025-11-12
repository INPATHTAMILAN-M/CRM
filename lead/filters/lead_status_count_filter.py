import django_filters

from accounts.models import Teams 
from ..models import Opportunity, Lead_Source, Lead_Status, Opportunity_Status, User
from django.db.models import Q

class OpportunityStatusFilter(django_filters.FilterSet):
    created_by = django_filters.NumberFilter(field_name="lead__created_by", lookup_expr="exact")
    assigned_to = django_filters.NumberFilter(field_name="lead__assigned_to", lookup_expr="exact")
    lead_source = django_filters.ModelChoiceFilter(queryset=Lead_Source.objects.all(), field_name='lead__lead_source')
    opp_status = django_filters.CharFilter(field_name='opportunity_status__name', lookup_expr='exact')
    opportunity_status = django_filters.ModelChoiceFilter(queryset=Lead_Status.objects.all())
    bdm = django_filters.BaseInFilter(method="filter_bdm")
    bde = django_filters.ModelChoiceFilter(queryset=User.objects.all(), method='filter_bde', label="BDE Filter")
    from_date = django_filters.DateFilter(field_name="lead__created_on", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="lead__created_on", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")


    role_asssigned = django_filters.ModelChoiceFilter(queryset=User.objects.all(),method='filter_role_assigned', label="BDM Assigned")
    assigned_leads =  django_filters.BooleanFilter(method='filter_assigned_leads', label="Assigned Leads")
    team = django_filters.BooleanFilter(method='filter_team', label="Team Filter")

    class Meta:
        model = Opportunity
        fields = [
            "created_by",
            "assigned_to",
            "lead_source",
            "opportunity_status",
            "from_date",
            "to_date",
            "bdm",
            "bde",
            'opp_status'
        ]


    def filter_role_assigned(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(lead__assigned_to=self.request.user) & Q(lead__created_by=value)
            )
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

    def filter_search(self, queryset, name, value):
        """Search by lead name or opportunity name."""
        return queryset.filter(
            Q(name__name__icontains=value) |  
            Q(lead__name__icontains=value)  
        )
    
    def filter_assigned_leads(self, queryset, name, value):
        if value:
            return queryset.filter(lead__assigned_to__isnull=False)
        return queryset
    
    def filter_team(self, queryset, name, value):
        """
        Filters queryset based on team relationships.
        Handles ?team=true/false flag.
        """
        request = self.request
        user = request.user

        is_admin = user.groups.filter(name__iexact="Admin").exists()
        is_bdm = user.groups.filter(name__iexact="BDM").exists()

        # --- Case 1: Admin ---
        # Admins can see all except their own created records
        if is_admin:
            return queryset.exclude(created_by=user)

        # --- Case 2: BDM ---
        # BDM can see their team's leads when team=true, else their own
        if is_bdm:
            user_team = Teams.objects.filter(bdm_user=user).first()
            if not user_team:
                return queryset.none()

            # When ?team=true → include all team members' leads (not BDM’s own)
            if str(value).lower() == "true":
                team_member_ids = list(user_team.bde_user.values_list("id", flat=True))

                return queryset.filter(
                    Q(lead__assigned_to__in=team_member_ids) |
                    Q(lead__created_by__in=team_member_ids)
                )

            # When ?team=false → only show own records
            return queryset.filter(
                Q(lead__assigned_to=user.id) |
                Q(lead__created_by=user.id)
            )

        # --- Case 3: Regular user (BDE etc.) ---
        return queryset.filter(
            Q(lead__assigned_to=user.id) |
            Q(lead__created_by=user.id)
        )

    