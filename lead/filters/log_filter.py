
import django_filters
from django.db import models
from ..models import Lead_Status, Log,Lead,Contact,Opportunity,Focus_Segment,Log_Stage


class LogFilter(django_filters.FilterSet):
    created_on = django_filters.DateFromToRangeFilter() 
    contact = django_filters.ModelChoiceFilter(queryset=Contact.objects.all())
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())
    opportunity = django_filters.ModelChoiceFilter(queryset=Opportunity.objects.all())
    details = django_filters.CharFilter(field_name='details', lookup_expr='icontains')
    log_stage = django_filters.ModelChoiceFilter(queryset=Log_Stage.objects.all())
    focus_segment = django_filters.ModelChoiceFilter(queryset=Focus_Segment.objects.all())
    is_active = django_filters.BooleanFilter()
    
    
    class Meta:
        model = Log
        fields = ['contact', 'lead', 'opportunity', 'focus_segment', 'log_stage', 
                 'created_by', 'is_active','lead_log_status']
    
