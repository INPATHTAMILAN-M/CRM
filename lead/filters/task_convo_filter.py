from django_filters import rest_framework as filters
from ..models import TaskConversationLog

class TaskConversationLogFilter(filters.FilterSet):
    task = filters.BaseInFilter(field_name='task__id')
    created_by = filters.BaseInFilter(field_name='created_by__id')
    created_on = filters.DateFromToRangeFilter()
    

    class Meta:
        model = TaskConversationLog
        fields = ['task', 'created_by', 'created_on']