from django_filters import rest_framework as filters
from django.contrib.auth.models import User

from accounts.models import Teams
from ..models import Task, TaskConversationLog
from django.utils import timezone
from django.db.models import Q


class TaskFilter(filters.FilterSet):

    lead = filters.NumberFilter(field_name='contact__lead__id')   
    contact = filters.CharFilter(field_name='contact__name', lookup_expr='icontains', label='Contact Name') 
    from_date = filters.DateFilter(field_name='task_date_time', lookup_expr='gte', label='From Date')
    to_date = filters.DateFilter(field_name='task_date_time', lookup_expr='lte', label='To Date', required=False)
    assigned_to_me = filters.BooleanFilter(field_name='task_task_assignments__assigned_to', method='filter_assigned_to_me')
    assigned_to = filters.NumberFilter(field_name='task_task_assignments__assigned_to',method='filter_assigned_to',label='Assigned To User ID')
    assigned_by_me = filters.BooleanFilter(field_name='task_task_assignments__assigned_by', method='filter_assigned_by_me')
    
    has_reply = filters.BooleanFilter(field_name='task_conversation_logs__task', method='filter_has_reply')

    team = filters.BooleanFilter(method='filter_team', label="Team Filter")

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
        user = self.request.user  # Ensure 'self' has 'request'
        
        if value:  # If True, filter tasks assigned to the user but not assigned by them
            return queryset.filter(
                Q(task_task_assignments__assigned_to=user) & 
                ~Q(task_task_assignments__assigned_by=user)  # Fix negation
            ).distinct()
        
        return queryset 
    
    def filter_assigned_to(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(task_task_assignments__assigned_to_id=value)
                & ~Q(task_task_assignments__assigned_by_id=value)
            ).distinct()
        return queryset

    def filter_assigned_by_me(self, queryset, name, value):
        # Get logged-in user
        user = self.request.user
        if value:  # If value is True, filter tasks assigned by the user
            return queryset.filter(task_task_assignments__assigned_by=user).distinct()
        return queryset  # Return all if False or None


    def filter_search(self, queryset, name, value):
        return queryset.filter(task_detail__icontains=value)
    
    def filter_team(self, queryset, name, value):
        """
        Filters queryset based on team relationships.
        Handles ?team=true/false flag.
        """
        request = self.request
        user = request.user

        is_admin = user.groups.filter(name__iexact="Admin").exists()
        is_bdm = user.groups.filter(name__iexact="BDM").exists()

        # --- Case 1: Admin ---
        # Admins can see all except their own created records
        if is_admin:
            return queryset.exclude(task_task_assignments__assigned_to=user)

        # --- Case 2: BDM ---
        # BDM can see their team's leads when team=true, else their own
        if is_bdm:
            user_team = Teams.objects.filter(bdm_user=user).first()
            if not user_team:
                return queryset.none()

            # When ?team=true → include all team members' leads (not BDM’s own)
            if str(value).lower() == "true":
                team_member_ids = list(user_team.bde_user.values_list("id", flat=True))

                return queryset.filter(
                    Q(task_task_assignments__assigned_to__in=team_member_ids) |
                    Q(created_by=team_member_ids)
                )

            # When ?team=false → only show own records
            return queryset.filter(
                Q(lead__assigned_to=user.id) |
                Q(created_by=user.id)
            )

        # --- Case 3: Regular user (BDE etc.) ---
        return queryset.filter(
            Q(lead__assigned_to=user.id) |
            Q(created_by=user.id)
        )

    class Meta:
        model = Task
        fields = ['is_active', 'created_on', 'lead',
                 'task_date_time', 'task_detail', 'created_by', 'task_type',
                 'contact', 'log', ]
        
    

