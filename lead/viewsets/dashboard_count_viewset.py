from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import Teams
from ..models import Opportunity_Status, Opportunity
from lead.filters.lead_status_count_filter import OpportunityStatusFilter  # Import the filter

class LeadStatusCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OpportunityStatusFilter

    def list(self, request):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())  # Apply filters

        # Determine user access
        if user.groups.filter(name='Admin').exists():
            opportunity = queryset

        elif user.groups.filter(name='BDM').exists():
            bde_users = Teams.objects.filter(bdm_user=user).values_list('bde_user', flat=True)
            opportunity = queryset.filter(
                Q(lead__lead_owner=user) | Q(lead__created_by=user) | Q(lead__assigned_to__in=bde_users),
                lead__is_active=True
            )
        elif user.groups.filter(name__in=['TM', 'BDE']).exists():
            opportunity = queryset.filter(
                Q(lead__assigned_to=user) | Q(lead__created_by=user),
                lead__is_active=True
            )
        elif user.groups.filter(name='DM').exists():
            opportunity = queryset.filter(lead__created_by=user)
        else:
            opportunity = queryset.none()

        # Get today's date
        today = timezone.now().date()
        # from_date = request.query_params.get("from_date")
        
        # if from_date:
        #     from_date = timezone.datetime.strptime(from_date, '%Y-%m-%d').date()
        # else:
        #     from_date = today.replace(day=1)  # Default to first day of the month

        # Exclude None values before aggregation
        opportunity_status_counts = (
            opportunity.exclude(opportunity_status=None)
            .values('opportunity_status__name')
            .annotate(
                today_count=Count('id', filter=Q(lead__created_on=today) | Q(status_date=today)),
                this_month_count=Count('id', filter=Q(lead__created_on__month=timezone.now().month) | Q(status_date__month=timezone.now().month))
            )
        )

        # Prepare result dictionary
        opportunity_statuses = Opportunity_Status.objects.values_list('name', flat=True)
        result = {status: {"today": 0, "this_month": 0} for status in opportunity_statuses}

        for entry in opportunity_status_counts:
            if entry['opportunity_status__name']:  # Ensure it's not None
                result[entry['opportunity_status__name']] = {
                    "today": entry["today_count"],
                    "this_month": entry["this_month_count"]
                }

        return Response(result, status=status.HTTP_200_OK)
