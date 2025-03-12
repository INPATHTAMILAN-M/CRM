from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import Teams
from ..models import  Opportunity, Lead_Status
from lead.filters.lead_status_count_filter import OpportunityStatusFilter  # Import the filter

class LeadStatusCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = OpportunityStatusFilter

    def list(self, request):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())  # Apply filters

        # Get current date details
        today = timezone.now().date()
        now = timezone.now()

        # Debugging: Print counts for verification
        print("Filtered Total (This Month):", queryset.filter(
            
            Q(lead__created_on__year=now.year, lead__created_on__month=now.month) |
            Q(status_date__year=now.year, status_date__month=now.month)
        ).count())

        # Aggregate opportunity status counts
        opportunity_status_counts = (
            queryset.exclude(opportunity_status=None)
            .values('opportunity_status__id', 'opportunity_status__name')
            .annotate(
                today_count=Count('id', filter=Q(lead__created_on=today) | Q(status_date=today)),
                this_month_count=Count('id', filter=Q(lead__created_on__year=now.year, lead__created_on__month=now.month) |
                                       Q(status_date__year=now.year, status_date__month=now.month))
            )
        )

        # Fetch all possible statuses
        opportunity_statuses = Lead_Status.objects.values('id', 'name')
        result = {status["name"]: {"id": status["id"], "today": 0, "this_month": 0} for status in opportunity_statuses}

        # Fill result with aggregated counts
        for entry in opportunity_status_counts:
            if entry['opportunity_status__name']:  # Ensure it's not None
                result[entry['opportunity_status__name']] = {
                    "id": entry["opportunity_status__id"],
                    "today": entry["today_count"],
                    "this_month": entry["this_month_count"]
                }

        return Response(result, status=status.HTTP_200_OK)

