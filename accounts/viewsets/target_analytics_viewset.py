from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from accounts.models import MonthlyTarget
from accounts.serializers.target_analytics_serializer import TargetAnalyticsSerializer
from lead.models import Opportunity, Lead_Status


class TargetAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for target analytics calculations.
    Provides endpoint to get target vs achieved data for previous, current, next month and annual.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='analytics')
    def get_analytics(self, request):
        """
        Get target analytics for authenticated user.
        Calculates achieved amounts from opportunities where user is owner or created_by.
        
        Returns data for:
        - Previous month
        - Current month
        - Next month
        - Annual (current year)
        """
        user = request.user
        today = date.today()
        
        # Calculate months
        current_month = today.month
        current_year = today.year
        
        prev_date = today - relativedelta(months=1)
        prev_month = prev_date.month
        prev_year = prev_date.year
        
        next_date = today + relativedelta(months=1)
        next_month = next_date.month
        next_year = next_date.year
        
        # Helper function to get opportunities for a user in a specific month/year
        def get_achieved_amount(month, year):
            """
            Calculate total opportunity value for opportunities where:
            The lead is either created_by or assigned_to the user
            And opportunity closing_date is in the specified month/year
            """
            opportunities = Opportunity.objects.filter(
                Q(lead__created_by=user) | Q(lead__assigned_to=user),
                closing_date__month=month,
                closing_date__year=year,
                is_active=True
            )
            
            total = opportunities.aggregate(
                total_value=Sum('opportunity_value')
            )['total_value']
            
            return Decimal(total) if total else Decimal('0.00')
        
        # Helper function to get target for a specific month/year
        def get_target_amount(month, year):
            """Get monthly target for user"""
            try:
                target = MonthlyTarget.objects.get(
                    user=user,
                    month=month,
                    year=year
                )
                return target.target_amount
            except MonthlyTarget.DoesNotExist:
                return Decimal('0.00')
        
        # Helper function to calculate percentage
        def calculate_percentage(achieved, target):
            """Calculate achievement percentage"""
            if target and target > 0:
                percentage = (achieved / target) * 100
                return int(round(percentage))
            return 0
        
        # Helper function to determine if there's an increase
        def calculate_increase(current_achieved, previous_achieved):
            """Determine if current achieved is more than previous"""
            return current_achieved > previous_achieved
        
        # Previous Month Data
        prev_target = get_target_amount(prev_month, prev_year)
        prev_achieved = get_achieved_amount(prev_month, prev_year)
        prev_percentage = calculate_percentage(prev_achieved, prev_target)
        
        # Get month before previous for comparison
        two_months_ago = today - relativedelta(months=2)
        two_months_ago_achieved = get_achieved_amount(two_months_ago.month, two_months_ago.year)
        prev_increase = calculate_increase(prev_achieved, two_months_ago_achieved)
        
        # Current Month Data
        current_target = get_target_amount(current_month, current_year)
        current_achieved = get_achieved_amount(current_month, current_year)
        current_percentage = calculate_percentage(current_achieved, current_target)
        current_increase = calculate_increase(current_achieved, prev_achieved)
        
        # Next Month Data
        next_target = get_target_amount(next_month, next_year)
        next_achieved = Decimal('0.00')  # Future month, no achieved yet
        next_percentage = 0
        next_increase = False
        
        # Annual Data (current year)
        annual_target = Decimal('0.00')
        annual_achieved = Decimal('0.00')
        
        # Sum all monthly targets for current year
        annual_targets = MonthlyTarget.objects.filter(
            user=user,
            year=current_year
        )
        for target in annual_targets:
            annual_target += target.target_amount
        
        # Sum all achieved opportunities for current year
        annual_opportunities = Opportunity.objects.filter(
            Q(lead__created_by=user) | Q(lead__assigned_to=user),
            closing_date__year=current_year,opportunity_status=34,
            is_active=True
        )
        annual_total = annual_opportunities.aggregate(
            total_value=Sum('opportunity_value')
        )['total_value']
        annual_achieved = Decimal(annual_total) if annual_total else Decimal('0.00')
        
        annual_percentage = calculate_percentage(annual_achieved, annual_target)
        
        # Get last year's achieved for comparison
        last_year_opportunities = Opportunity.objects.filter(
            Q(lead__created_by=user) | Q(lead__assigned_to=user),
            closing_date__year=current_year - 1,
            is_active=True
        )
        last_year_total = last_year_opportunities.aggregate(
            total_value=Sum('opportunity_value')
        )['total_value']
        last_year_achieved = Decimal(last_year_total) if last_year_total else Decimal('0.00')
        annual_increase = calculate_increase(annual_achieved, last_year_achieved)
        
        # Build response data
        analytics_data = [
            {
                'type': 'prevMonth',
                'title': 'Previous Month',
                'subtitle': 'Target vs Achieved',
                'target': prev_target,
                'achieved': prev_achieved,
                'percentage': prev_percentage,
                'increase': prev_increase
            },
            {
                'type': 'currentMonth',
                'title': 'Current Month',
                'subtitle': 'Target vs Achieved',
                'target': current_target,
                'achieved': current_achieved,
                'percentage': current_percentage,
                'increase': current_increase
            },
            {
                'type': 'nextMonth',
                'title': 'Next Month',
                'subtitle': 'Upcoming Target',
                'target': next_target,
                'achieved': next_achieved,
                'percentage': next_percentage,
                'status': 'Upcoming',
                'increase': next_increase
            },
            {
                'type': 'annual',
                'title': 'Annual Target',
                'subtitle': 'Your Yearly Goal',
                'target': annual_target,
                'achieved': annual_achieved,
                'percentage': annual_percentage,
                'increase': annual_increase
            }
        ]
        
        # Serialize the data
        serializer = TargetAnalyticsSerializer(analytics_data, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
