import django_filters
from django.contrib.auth.models import User
from django.db.models import Q

from accounts.models import Lead_Source, Teams
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
    created_by = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        method='filter_created_by_or_assigned_to',
        label="Created By Filter"
    )
    assigned_to_by_contact = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all(), field_name='assigned_to', label="Assigned To Filter")
    
    team = django_filters.BooleanFilter(method='filter_team', label="Team Filter")
    
    
    class Meta:
        model = Contact
        fields = ['name', 'lead', 'is_active', 'status', 'is_archive', 'lead_is_null', 'assigned_to', 'lead_source', 
                  'from_date', 'to_date', 'lead_status', 'created_by', 'assigned_to_by_contact']
    
    def filter_lead_is_null(self, queryset, name, value):
        if value:
            return queryset.filter(lead__isnull=True)  
        return queryset
    
    def filter_created_by_or_assigned_to(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(created_by__in=value) | Q(assigned_to__in=value)
            )
        return queryset
    
    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(company_name__icontains=value) |
            Q(phone_number__icontains=value)
        )
    
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
