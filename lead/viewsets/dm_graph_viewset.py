from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from lead.serializers.dm_graph_serializer import LeadCountRequestSerializer
from ..models import Lead

class LeadCountViewSet(viewsets.ViewSet):
    """
    A simple ViewSet to get lead counts by date or month.
    """
    
    def list(self, request):
        # Validate the input data
        serializer = LeadCountRequestSerializer(data=request.query_params)
        if serializer.is_valid():
            from_date = serializer.validated_data['from_date']
            to_date = serializer.validated_data['to_date']

            # Ensure that from_date and to_date are datetime objects (to ensure they are in correct format)
            from_date = timezone.datetime.strptime(str(from_date), "%Y-%m-%d")
            to_date = timezone.datetime.strptime(str(to_date), "%Y-%m-%d")

            # Check if the range is within 31 days
            if (to_date - from_date).days <= 31:
                # Group leads by date
                lead_counts_by_date = (
                    Lead.objects.filter(created_by= request.user,created_on__range=[from_date, to_date])
                    .values('created_on')
                    .annotate(lead_count=Count('id'))
                    .order_by('created_on')
                )

                # Generate a set of all dates in the range
                all_dates = {from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)}

                # Create a dictionary with counts, filling in missing dates with a count of 0
                result = { (from_date + timedelta(days=i)).strftime('%d-%m-%Y'): 0 for i in range((to_date - from_date).days + 1) }

                # Populate the result with actual counts
                for lead in lead_counts_by_date:
                    result[lead['created_on'].strftime('%d-%m-%Y')] = lead['lead_count']

                sorted_result = dict(sorted(result.items()))

                return Response(sorted_result)

            else:
                # Group leads by month
                lead_counts_by_month = (
                    Lead.objects.filter(created_on__range=[from_date, to_date])
                    .values('created_on__year', 'created_on__month')
                    .annotate(lead_count=Count('id'))
                    .order_by('created_on__year', 'created_on__month')
                )

                # Generate a set of all months in the range
                all_months = []
                current_month = from_date.replace(day=1)
                while current_month <= to_date:
                    all_months.append((current_month.year, current_month.month))
                    # Move to the next month
                    if current_month.month == 12:
                        current_month = timezone.datetime(current_month.year + 1, 1, 1)
                    else:
                        current_month = timezone.datetime(current_month.year, current_month.month + 1, 1)

                # Create a dictionary with counts, filling in missing months with a count of 0
                result = {timezone.datetime(year, month, 1).strftime('%B'): 0 for year, month in all_months}

                # Populate the result with actual counts
                for lead in lead_counts_by_month:
                    month_name = timezone.datetime(lead['created_on__year'], lead['created_on__month'], 1).strftime('%B')
                    result[month_name] = lead['lead_count']

                return Response(result)

        return Response(serializer.errors, status=400)