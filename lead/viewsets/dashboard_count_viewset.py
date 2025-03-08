from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from accounts.models import Teams
from ..models import Opportunity, Lead_Status
from lead.filters.lead_status_count_filter import OpportunityStatusFilter  

class LeadStatusCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OpportunityStatusFilter

    def list(self, request):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset())  # Apply filters

        # Filter opportunities based on user role
        if user.groups.filter(name='Admin').exists():
            opportunity = queryset
        elif user.groups.filter(name='BDM').exists():
            bde_users = Teams.objects.filter(bdm_user=user).values_list('bde_user', flat=True)
            opportunity = queryset.filter(
                Q(lead__lead_owner=user) | Q(lead__created_by=user) | Q(lead__assigned_to__in=bde_users),
                lead__is_active=True
            )
        elif user.groups.filter(name__in=['TM', 'BDE']).exists():
            opportunity = queryset.filter(Q(lead__assigned_to=user) | Q(lead__created_by=user), lead__is_active=True)
        elif user.groups.filter(name='DM').exists():
            opportunity = queryset.filter(lead__created_by=user)
        else:
            opportunity = queryset

        today = timezone.now().date()

        # Get opportunity status counts
        counts = opportunity.exclude(opportunity_status=None).values('opportunity_status__id', 'opportunity_status__name').annotate(
            today_count=Count('id', filter=Q(lead__created_on=today) | Q(status_date=today)),
            this_month_count=Count('id', filter=Q(lead__created_on__month=today.month) | Q(status_date__month=today.month))
        )

        # Convert to dictionary for easy lookup
        status_counts = {entry['opportunity_status__id']: entry for entry in counts}

        # Prepare final result
        result = [
            {
                "id": status.id,
                "name": status.name,
                "today": status_counts.get(status.id, {}).get("today_count", 0),
                "this_month": status_counts.get(status.id, {}).get("this_month_count", 0)
            }
            for status in Lead_Status.objects.all()
        ]

        return Response(result, status=status.HTTP_200_OK)
