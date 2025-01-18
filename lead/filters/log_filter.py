
import django_filters
from ..models import  Log,Lead,Contact,Opportunity,Log_Stage
from django.db.models import Q

class LogFilter(django_filters.FilterSet):
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())
    opportunity = django_filters.ModelChoiceFilter(queryset=Opportunity.objects.all())
    log_stage = django_filters.ModelChoiceFilter(queryset=Log_Stage.objects.all())
    log_type = django_filters.ChoiceFilter(choices=Log.LOG_TYPE_CHOICES, null_label='All', label='Log Type')
    include_opportunity = django_filters.ModelChoiceFilter(queryset=Lead.objects.all(), method='filter_by_lead_and_opportunity')

    class Meta:
        model = Log
        fields = ['contact', 'lead', 'opportunity', 'log_stage','log_type']
        
    def filter_by_lead_and_opportunity(self, queryset, name, value):
        if value:
            # Get the lead instance
            lead = value
            
            # Get all opportunities related to this lead
            opportunities = Opportunity.objects.filter(lead=lead)
            
            # Filter logs by the given lead or its associated opportunities
            return queryset.filter(Q(lead=lead) | Q(opportunity__in=opportunities))
        
        return queryset