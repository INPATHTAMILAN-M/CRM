
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.utils import timezone
from datetime import datetime
from accounts.models import Teams
from lead.filters.lead_filter import LeadFilter
from ..models import Lead  # Adjust import if needed
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

class LeadStatusCountViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        # Get the current user
        user = self.request.user
        created_by = request.query_params.get('created_by',None)
        assigned_to = request.query_params.get('assigned_to',None)
        lead_source = request.query_params.get('lead_source',None)
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        lead_status = request.query_params.get('lead_status',None)
        bdm = request.query_params.get('bdm',None)
        bde = request.query_params.get('bde',None)
        search = request.query_params.get('search',None)
        
        
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
            # Admin can see all leads
            leads = Lead.objects.all()
        elif user.groups.filter(name='BDM').exists():
            # BDM should filter by lead_owner
            bde_users = Teams.objects.filter(bdm_user=user).values_list('bde_user', flat=True)
            leads = Lead.objects.filter(
                Q(lead_owner=user) | Q(created_by=user) | Q(created_by__in=bde_users) | Q(assigned_to__in=bde_users) & Q(is_active=True)
            ).order_by('-id')
        elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
            # TM or BDE should filter by assigned_to
            leads = Lead.objects.filter(Q(assigned_to=user) | Q(created_by=user) & Q(is_active=True))
        elif user.groups.filter(name='DM').exists():
            # DM should filter by created_by
            leads = Lead.objects.filter(created_by=user)
        else:
            # For other cases, no data is returned
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

        # Apply the date range filter if from_date and to_date are provided
        if from_date and to_date:
            filter_conditions &= Q(created_on__range=[from_date, to_date])
        elif from_date:
            filter_conditions &= Q(created_on__gte=from_date)
        elif to_date:
            filter_conditions &= Q(created_on__lte=to_date)

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
        # Build the result in the required format
        result = {}
        for entry in lead_status_counts:
            result[entry['lead_status__name']] = {
                "today": entry['today_count'],
                "this_month": entry['this_month_count']
            }

        return Response(result, status=status.HTTP_200_OK)