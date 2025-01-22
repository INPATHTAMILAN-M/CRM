
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.utils import timezone
from datetime import datetime
from accounts.models import Teams
from lead.filters.lead_filter import LeadFilter
from ..models import Lead, Lead_Status  # Adjust import if needed
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

class LeadStatusCountViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        # Get the current user
        user = self.request.user
        created_by = request.query_params.get('created_by', None)
        assigned_to = request.query_params.get('assigned_to', None)
        lead_source = request.query_params.get('lead_source', None)
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        lead_status = request.query_params.get('lead_status', None)
        bdm = request.query_params.get('bdm', None)
        bde = request.query_params.get('bde', None)
        search = request.query_params.get('search', None)
        
        # Parse date range if available
        if from_date:
            if to_date:
                to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
            else:
                to_date = timezone.now()
        else:
            from_date = None
            to_date = None

        # Define the query based on the user's group
        if user.groups.filter(name='Admin').exists():
            leads = Lead.objects.all()
        elif user.groups.filter(name='BDM').exists():
            bde_users = Teams.objects.filter(bdm_user=user).values_list('bde_user', flat=True)
            leads = Lead.objects.filter(
                Q(lead_owner=user) | Q(created_by=user) | Q(created_by__in=bde_users) | Q(assigned_to__in=bde_users) & Q(is_active=True)
            ).order_by('-id')
        elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
            leads = Lead.objects.filter(Q(assigned_to=user) | Q(created_by=user) & Q(is_active=True))
        elif user.groups.filter(name='DM').exists():
            leads = Lead.objects.filter(created_by=user)
        else:
            leads = Lead.objects.none()

        # Get today's date and the first day of the current month
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)

        filter_conditions = Q()

        if created_by:
            filter_conditions &= Q(created_by=created_by)
        if assigned_to:
            filter_conditions &= Q(assigned_to=assigned_to)
        if lead_source:
            filter_conditions &= Q(lead_source=lead_source)
        if lead_status:
            filter_conditions &= Q(lead_status=lead_status)
        if bdm:
            filter_conditions &= Q(lead_owner__in=bdm) | Q(created_by__in=bdm)
        if bde:
            filter_conditions &= Q(assigned_to=bde) | Q(created_by=bde)
        if search:
            filter_conditions &= (Q(name__icontains=search) | Q(company_website__icontains=search))

        if from_date and to_date:
            filter_conditions &= Q(created_on__range=[from_date, to_date])
        elif from_date:
            filter_conditions &= Q(created_on__gte=from_date)
        elif to_date:
            filter_conditions &= Q(created_on__lte=to_date)

        # Get all lead statuses from the Lead_Status model
        all_lead_statuses = Lead_Status.objects.all()

        # Query to get counts for each lead_status, filtered by the user's leads
        lead_status_counts = leads.filter(filter_conditions).values('lead_status__name').annotate(
            today_count=Count(
                'id', 
                filter=Q(created_on=today) | Q(status_date=today)
            ),
            this_month_count=Count(
                'id', 
                filter=Q(created_on__gte=first_day_of_month) | Q(status_date__gte=first_day_of_month)
            )
        )

        # Initialize the result dictionary with all possible lead statuses, all with zero counts
        result = {status.name: {"today": 0, "this_month": 0} for status in all_lead_statuses}

        # Update the result with actual counts from the database
        for entry in lead_status_counts:
            lead_status_name = entry['lead_status__name']
            if lead_status_name in result:
                result[lead_status_name] = {
                    "today": entry['today_count'],
                    "this_month": entry['this_month_count']
                }

        return Response(result, status=status.HTTP_200_OK)