from django_filters import rest_framework as filters
from django.contrib.auth.models import User
from ..models import Task, TaskConversationLog
import django_filters
from django.utils import timezone

class TaskFilter(filters.FilterSet):

    lead = filters.NumberFilter(field_name='contact__lead__id')   
    contact = filters.CharFilter(field_name='contact__name', lookup_expr='icontains', label='Contact Name') 
    from_date = filters.DateFilter(field_name='created_on', lookup_expr='gte', label='From Date')
    to_date = filters.DateFilter(field_name='created_on', lookup_expr='lte', label='To Date', required=False)
    assigned_to_me = filters.BooleanFilter(field_name='task_task_assignments__assigned_to', method='filter_assigned_to_me')
    assigned_by_me = filters.BooleanFilter(field_name='task_task_assignments__assigned_by', method='filter_assigned_by_me')
    has_reply = filters.BooleanFilter(field_name='task_conversation_logs__task', method='filter_has_reply')

    def filter_has_reply(self, queryset, name, value):
        if value:
            # Find tasks with conversation logs (replies) by filtering through task_conversation_logs
            tasks_with_replies = TaskConversationLog.objects.filter(task__in=queryset).values_list('task', flat=True)
            return queryset.filter(id__in=tasks_with_replies).distinct()
        return queryset.order_by('-task_conversation_logs__created_on')   

    def filter_to_date(self, queryset, name, value):
        # If 'to_date' is not provided, default to today
        if not value:
            value = timezone.now().date()  # Use today's date
        return queryset.filter(created_on__lte=value)
    
    
    def filter_assigned_to_me(self, queryset, name, value):
        # Get logged-in user
        user = self.request.user
        if value:  # If value is True, filter tasks assigned to the user
            return queryset.filter(task_task_assignments__assigned_to=user).distinct()
        return queryset  # Return all if False or None

    # Custom method for filtering tasks assigned by the logged-in user
    def filter_assigned_by_me(self, queryset, name, value):
        # Get logged-in user
        user = self.request.user
        if value:  # If value is True, filter tasks assigned by the user
            return queryset.filter(task_task_assignments__assigned_by=user).distinct()
        return queryset  # Return all if False or None


    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)

    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead',
                 'task_date_time', 'task_detail', 'created_by', 'task_type',
                 'contact', 'log', ]
