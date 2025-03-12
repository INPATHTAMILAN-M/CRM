import django_filters 
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
            Q(name__icontains=value) |  
            Q(lead__name__icontains=value)  
        )
