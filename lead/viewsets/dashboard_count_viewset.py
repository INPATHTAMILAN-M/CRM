from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Lead, Lead_Status

class LeadStatusCountViewSet(viewsets.ViewSet):

    def get_queryset(self):
        # Get the current user
        user = self.request.user

        # Define filters based on the user's group
        if user.groups.filter(name='Admin').exists():
            # Admin can see all leads
            return Lead.objects.all()
        elif user.groups.filter(name='BDM').exists():
            # BDM should filter by lead_owner
            return Lead.objects.filter(lead_owner=user)
        elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
            # TM or BDE should filter by assigned_to
            return Lead.objects.filter(assigned_to=user)
        elif user.groups.filter(name='DM').exists():
            # DM should filter by created_by
            return Lead.objects.filter(created_by=user)
        else:
            # For other cases, no data is returned
            return Lead.objects.none()

    def get_lead_counts(self, queryset):
        """
        Helper method to count leads based on lead_status
        and return today's and this month's count for each lead status.
        """
        today = timezone.now().date()
        start_of_month = today.replace(day=1)

        # Prepare a dictionary to hold lead counts by lead_status
        lead_status_counts = {}

        # Get lead counts for today and this month, grouped by lead_status
        lead_statuses = Lead_Status.objects.all()

        for status in lead_statuses:
            # Filter leads based on the status and calculate the counts
            leads_today = queryset.filter(lead_status=status, created_on=today).count()
            leads_this_month = queryset.filter(lead_status=status, created_on__gte=start_of_month).count()

            lead_status_counts[status.name] = {
                'today': leads_today,
                'this_month': leads_this_month
            }

        return lead_status_counts

    def list(self, request):
        """
        Custom method to return the count of leads for each lead_status.
        """
        queryset = self.get_queryset()

        # Get lead status counts
        lead_status_counts = self.get_lead_counts(queryset)

        return Response(lead_status_counts)
