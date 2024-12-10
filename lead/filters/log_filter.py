
import django_filters
from django.db import models
from django_filters import DateFilter, CharFilter, ChoiceFilter, ModelChoiceFilter, BooleanFilter
from ..models import Log


class LogFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_on', lookup_expr='gte')
    end_date = DateFilter(field_name='created_on', lookup_expr='lte')
    contact_name = CharFilter(field_name='contact__name', lookup_expr='icontains')
    lead_name = CharFilter(field_name='lead__name', lookup_expr='icontains')
    opportunity_name = CharFilter(field_name='opportunity__name', lookup_expr='icontains')
    details = CharFilter(field_name='details', lookup_expr='icontains')
    logtype = ChoiceFilter(choices=[('Call', 'Call'), ('Meeting', 'Meeting'), ('Email', 'Email'), ('Others', 'Others')])
    log_stage = ModelChoiceFilter(queryset=None)
    focus_segment = ModelChoiceFilter(queryset=None)
    is_active = BooleanFilter()
    
    class Meta:
        model = Log
        fields = ['contact', 'lead', 'opportunity', 'focus_segment', 'log_stage', 
                 'created_by', 'is_active', 'logtype']
    
    def __init__(self, *args, **kwargs):
        super(LogFilter, self).__init__(*args, **kwargs)
        self.filters['log_stage'].queryset = Log_Stage.objects.all()
        self.filters['focus_segment'].queryset = Focus_Segment.objects.all()
