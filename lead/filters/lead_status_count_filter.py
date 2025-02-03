import django_filters 
from ..models import Opportunity, Lead_Source, Lead_Status, Opportunity_Status
from django.db.models import Q

class OpportunityStatusFilter(django_filters.FilterSet):
    created_by = django_filters.NumberFilter(field_name="lead__created_by", lookup_expr="exact")
    assigned_to = django_filters.NumberFilter(field_name="lead__assigned_to", lookup_expr="exact")
    lead_source = django_filters.ModelChoiceFilter(queryset=Lead_Source.objects.all(), field_name='lead__lead_source')
    opp_status = django_filters.CharFilter(field_name='opportunity_status__name', lookup_expr='exact')
    opportunity_status = django_filters.ModelChoiceFilter(queryset=Opportunity_Status.objects.all())
    bdm = django_filters.NumberFilter(method="filter_bdm")
    bde = django_filters.NumberFilter(method="filter_bde")
    from_date = django_filters.DateFilter(field_name="lead__created_on", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="lead__created_on", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")

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

    def filter_bdm(self, queryset, name, value):
        """Filter opportunities where the BDM is the lead owner or lead creator."""
        return queryset.filter(Q(lead__lead_owner=value) | Q(lead__created_by=value))

    def filter_bde(self, queryset, name, value):
        """Filter opportunities where the BDE is the assigned lead or lead creator."""
        return queryset.filter(Q(lead__assigned_to=value) | Q(lead__created_by=value))

    def filter_search(self, queryset, name, value):
        """Search by lead name or opportunity name."""
        return queryset.filter(
            Q(name__name__icontains=value) |  
            Q(lead__name__icontains=value)  
        )
