
import django_filters
from ..models import  Log,Lead,Contact,Opportunity,Log_Stage
from django.db.models import Q

class LogFilter(django_filters.FilterSet):
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())
    opportunity = django_filters.ModelChoiceFilter(queryset=Opportunity.objects.all())
    log_stage = django_filters.ModelChoiceFilter(queryset=Log_Stage.objects.all())
    log_type = django_filters.ChoiceFilter(choices=Log.LOG_TYPE_CHOICES, null_label='All', label='Log Type')
    include_opportunity = django_filters.NumberFilter(method='filter_by_opportunity')

    class Meta:
        model = Log
        fields = ['contact', 'lead', 'opportunity', 'log_stage','log_type']
        
    def filter_by_opportunity(self, queryset, name, value):
        if value:
            # Filter logs by the given opportunity ID (matching lead_id or contact's lead_id)
            return queryset.filter(
                Q(lead_id=value) | Q(contact__lead_id=value)
            )
        
        return queryset