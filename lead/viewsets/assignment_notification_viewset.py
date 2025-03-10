from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from lead.custom_pagination import Paginator
from ..models import Opportunity, Task, Task_Assignment, Lead, Lead_Assignment
from ..serializers.assignment_notification_serializer import OpportunityListSerializer, TaskListSerializer, LeadSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class LeadTaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AssignedNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LeadTaskPagination

    def get(self, request):
        user = request.user
        one_day_ago = timezone.now() + timedelta(days=1)
        search_query = request.query_params.get('search', None)
        type_query = request.query_params.get('type', None)

        # Initialize the combined data list
        combined_data = []

        # If 'type' is 'lead' or 'task', filter accordingly
        if type_query == 'lead':
            lead_assignments = Lead_Assignment.objects.filter(is_active=True,assigned_to=user, assigned_on=timezone.now().date())

            # Apply search filter if 'search' is provided
            if search_query:
                lead_assignments = lead_assignments.filter(lead__name__icontains=search_query)

            lead_ids = lead_assignments.values_list('lead_id', flat=True)
            leads = Lead.objects.filter(id__in=lead_ids)
            lead_serializer = LeadSerializer(leads, many=True)

            # Add 'type' information to each lead and append it to the combined_data list
            for lead in lead_serializer.data:
                lead['type'] = 'lead'
                # Check if 'assigned_on' is a string and convert it to date if needed
                assigned_on = lead_assignments.filter(lead=lead['id']).first().assigned_on
                if isinstance(assigned_on, str):
                    assigned_on = timezone.datetime.strptime(assigned_on, '%Y-%m-%dT%H:%M:%SZ').date()  # Convert ISO 8601 string to date
                lead['date'] = assigned_on
                combined_data.append(lead)
                
        elif type_query == 'opportunity':
            lead_assignments = Lead_Assignment.objects.filter(is_active=True,assigned_to=user)
            lead_ids = lead_assignments.values_list('lead_id', flat=True)
            leads = Lead.objects.filter(id__in=lead_ids)
            opportunities = Opportunity.objects.filter(lead__in=lead_ids)
            
            if search_query:
                opportunities = opportunities.filter(opportunity__name__icontains=search_query)

            opportunity_serializer = OpportunityListSerializer(opportunities, many=True)

            for opportunity in opportunity_serializer.data:
                opportunity['type'] = 'opportunity'
                assigned_on = opportunities.filter(opportunity=opportunity['id']).first().assigned_on
                if isinstance(assigned_on, str):
                    assigned_on = timezone.datetime.strptime(assigned_on, '%Y-%m-%dT%H:%M:%SZ').date()
                    
        elif type_query == 'task':
            task_assignments = Task_Assignment.objects.filter(is_active=True,assigned_to=user)

            # Apply search filter if 'search' is provided
            if search_query:
                task_assignments = task_assignments.filter(task__contact__lead__name__icontains=search_query)

            task_ids = task_assignments.values_list('task_id', flat=True)
            tasks = Task.objects.filter(
                Q(id__in=task_ids) & 
                (Q(task_date_time__date__lte=one_day_ago) | Q(task_date_time__date=timezone.now().date()))
            )
            task_serializer = TaskListSerializer(tasks, many=True)

            # Add 'type' information to each task and append it to the combined_data list
            for task in task_serializer.data:
                task['type'] = 'task'
                # Check if 'task_date_time' is a string and convert it to date if needed
                task_date_time = task['task_date_time']
                if isinstance(task_date_time, str):
                    task_date_time = timezone.datetime.strptime(task_date_time, '%Y-%m-%dT%H:%M:%SZ').date()  # Convert ISO 8601 string to date
                task['date'] = task_date_time
                combined_data.append(task)

        else:
            # If no type query is passed, show both leads and tasks
            lead_assignments = Lead_Assignment.objects.filter(is_active=True,assigned_to=user, assigned_on=timezone.now().date())

            if search_query:
                lead_assignments = lead_assignments.filter(lead__name__icontains=search_query)

            lead_ids = lead_assignments.values_list('lead_id', flat=True)
            leads = Lead.objects.filter(id__in=lead_ids)
            lead_serializer = LeadSerializer(leads, many=True)

            for lead in lead_serializer.data:
                lead['type'] = 'lead'
                assigned_on = lead_assignments.filter(lead=lead['id']).first().assigned_on
                if isinstance(assigned_on, str):
                    assigned_on = timezone.datetime.strptime(assigned_on, '%Y-%m-%dT%H:%M:%SZ').date()  # Convert ISO 8601 string to date
                lead['date'] = assigned_on
                combined_data.append(lead)

            task_assignments = Task_Assignment.objects.filter(is_active=True,assigned_to=user)

            if search_query:
                task_assignments = task_assignments.filter(task__contact__lead__name__icontains=search_query)

            task_ids = task_assignments.values_list('task_id', flat=True)
            tasks = Task.objects.filter(
                Q(id__in=task_ids) & 
                (Q(task_date_time__date__lte=one_day_ago) | Q(task_date_time__date=timezone.now().date()))
            )
            task_serializer = TaskListSerializer(tasks, many=True)

            for task in task_serializer.data:
                task['type'] = 'task'
                task_date_time = task['task_date_time']
                if isinstance(task_date_time, str):
                    task_date_time = timezone.datetime.strptime(task_date_time, '%Y-%m-%dT%H:%M:%SZ').date()  # Convert ISO 8601 string to date
                task['date'] = task_date_time
                combined_data.append(task)

        # Sort the combined data by date
        combined_data.sort(key=lambda x: x['date'], reverse=True)  # Sort by 'date' in descending order

        # Pagination for the combined data
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(combined_data, request)

        return paginator.get_paginated_response(paginated_data)