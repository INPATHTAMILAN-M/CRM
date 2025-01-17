
import django_filters
from django.db import models
from ..models import Lead_Status, Log,Lead,Contact,Opportunity,Focus_Segment,Log_Stage


class LogFilter(django_filters.FilterSet):
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())
    opportunity = django_filters.ModelChoiceFilter(queryset=Opportunity.objects.all())
    log_stage = django_filters.ModelChoiceFilter(queryset=Log_Stage.objects.all())
    log_type = django_filters.ChoiceFilter(choices=Log.LOG_TYPE_CHOICES, null_label='All', label='Log Type')
    
    class Meta:
        model = Log
        fields = ['contact', 'lead', 'opportunity', 'log_stage','log_type']
    