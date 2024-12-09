import django_filters
from lead.models import Lead
from accounts.models import Vertical, Focus_Segment

class LeadFilter(django_filters.FilterSet):
    vertical_id = django_filters.NumberFilter(field_name='focus_segment__vertical__id')  
    focus_segment = django_filters.ModelMultipleChoiceFilter(queryset=Focus_Segment.objects.all(), field_name='focus_segment__id', lookup_expr='in')
    market_segment = django_filters.ModelChoiceFilter(queryset=Lead.objects.values_list('market_segment', flat=True).distinct())  
    state = django_filters.ModelChoiceFilter(queryset=Lead.objects.values_list('state', flat=True).distinct()) 
    country = django_filters.ModelChoiceFilter(queryset=Lead.objects.values_list('country', flat=True).distinct())
    created_on = django_filters.DateFilter(field_name='created_on')
    annual_revenue = django_filters.NumberFilter(field_name='annual_revenue')  

    class Meta:
        model = Lead
        fields = ['vertical_id', 'focus_segment', 'market_segment', 'state', 'country', 'created_on', 'annual_revenue']