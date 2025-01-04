# from rest_framework import viewsets
# from rest_framework.response import Response
# from django.db.models import Count
# from django.contrib.auth.models import User
# from django.utils import timezone
# from ..models import Lead, Lead_Status

# class LeadStatusCountViewSet(viewsets.ViewSet):

#     def get_queryset(self):
#         # Get the current user
        # user = self.request.user

        # # Define filters based on the user's group
        # if user.groups.filter(name='Admin').exists():
        #     # Admin can see all leads
        #     return Lead.objects.all()
        # elif user.groups.filter(name='BDM').exists():
        #     # BDM should filter by lead_owner
        #     return Lead.objects.filter(lead_owner=user)
        # elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
        #     # TM or BDE should filter by assigned_to
        #     return Lead.objects.filter(assigned_to=user)
        # elif user.groups.filter(name='DM').exists():
        #     # DM should filter by created_by
        #     return Lead.objects.filter(created_by=user)
        # else:
        #     # For other cases, no data is returned
        #     return Lead.objects.none()

#     def get_lead_counts(self, queryset):
#         """
#         Helper method to count leads based on lead_status
#         and return today's and this month's count for each lead status.
#         """
#         today = timezone.now().date()
#         start_of_month = today.replace(day=1)

#         lead_status_counts = {}

#         lead_statuses = Lead_Status.objects.all()

#         for status in lead_statuses:
#             leads_today_created_on = queryset.filter(lead_status=status, created_on=today).count()
#             leads_this_month_created_on = queryset.filter(lead_status=status, created_on__gte=start_of_month).count()

#             leads_today_status_date = queryset.filter(lead_status=status, status_date=today).count()
#             leads_this_month_status_date = queryset.filter(lead_status=status, status_date__gte=start_of_month).count()

#             total_leads_today = leads_today_created_on + leads_today_status_date
#             total_leads_this_month = leads_this_month_created_on + leads_this_month_status_date

#             lead_status_counts[status.name] = {
#                 'today': total_leads_today,
#                 'this_month': total_leads_this_month
#             }

#         return lead_status_counts

#     def list(self, request):
#         """
#         Custom method to return the count of leads for each lead_status.
#         """
#         queryset = self.get_queryset()

#         # Get lead status counts
#         lead_status_counts = self.get_lead_counts(queryset)

#         return Response(lead_status_counts)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.utils import timezone
from ..models import Lead  # Adjust import if needed
from django.db.models import Q

# class LeadStatusCountViewSet(viewsets.ViewSet):
    
#     def list(self, request, *args, **kwargs):
#         # Get today's date and the first day of the current month
#         today = timezone.now().date()
#         first_day_of_month = today.replace(day=1)

#         # Query to get counts for each lead_status
#         lead_status_counts = Lead.objects.values('lead_status__name').annotate(
#             today_count=Count(
#                 'id', 
#                 filter=Q(created_on=today) | Q(status_date=today)
#             ),
#             this_month_count=Count(
#                 'id', 
#                 filter=Q(created_on__gte=first_day_of_month) | Q(status_date__gte=first_day_of_month)
#             )
#         )

#         # Build the result in the required format
#         result = {}
#         for entry in lead_status_counts:
#             result[entry['lead_status__name']] = {
#                 "today": entry['today_count'],
#                 "this_month": entry['this_month_count']
#             }

#         return Response(result, status=status.HTTP_200_OK)

class LeadStatusCountViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        # Get the current user
        user = self.request.user

        # Define the query based on the user's group
        if user.groups.filter(name='Admin').exists():
            # Admin can see all leads
            leads = Lead.objects.all()
        elif user.groups.filter(name='BDM').exists():
            # BDM should filter by lead_owner
            leads = Lead.objects.filter(lead_owner=user)
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

        # Query to get counts for each lead_status, filtered by the user's leads
        lead_status_counts = leads.values('lead_status__name').annotate(
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