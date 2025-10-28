from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP

from accounts.models import MonthlyTarget
from accounts.serializers.target_analytics_serializer import TargetAnalyticsSerializer
from lead.models import Opportunity


class TargetAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for target analytics calculations.
    Provides endpoint to get target vs achieved data for previous, current, next month and annual.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='analytics')
    def get_analytics(self, request):
        """
        Get target analytics for authenticated or filtered user.
        Admins can filter by ?user_id=.
        """
        user = request.user

        # ✅ If user is admin (based on group), allow filtering
        if user.groups.filter(name__iexact="admin").exists():
            user_id = request.query_params.get("user_id")
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        current_month, current_year = today.month, today.year

        prev_date = today - relativedelta(months=1)
        next_date = today + relativedelta(months=1)

        # ✅ Helper: safely calculate percentage (Decimal-safe)
        def pct(achieved, target):
            try:
                achieved = Decimal(str(achieved))
                target = Decimal(str(target))
            except Exception:
                return 0
            if target > 0:
                percentage = (achieved / target) * 100
                return int(percentage.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            return 0

        # ✅ Helper: check increase
        def inc(current, prev):
            return current > prev

        # ✅ Helper: achieved amount per month/year
        def get_achieved(month, year):
            qs = Opportunity.objects.filter(
                Q(lead__created_by=user) | Q(lead__assigned_to=user),
                closing_date__month=month,
                closing_date__year=year,
                opportunity_status=34,
                is_active=True
            ).aggregate(total=Sum("opportunity_value"))
            return Decimal(qs["total"] or 0)

        # ✅ Helper: monthly target
        def get_target(month, year):
            try:
                return MonthlyTarget.objects.get(user=user, month=month, year=year).target_amount
            except MonthlyTarget.DoesNotExist:
                return Decimal("0.00")

        # --- Previous Month ---
        prev_target = get_target(prev_date.month, prev_date.year)
        prev_ach = get_achieved(prev_date.month, prev_date.year)
        two_months_ago = today - relativedelta(months=2)
        two_months_ago_ach = get_achieved(two_months_ago.month, two_months_ago.year)
        prev_inc = inc(prev_ach, two_months_ago_ach)

        # --- Current Month ---
        curr_target = get_target(current_month, current_year)
        curr_ach = get_achieved(current_month, current_year)
        curr_inc = inc(curr_ach, prev_ach)

        # --- Next Month ---
        next_target = get_target(next_date.month, next_date.year)
        next_ach = Decimal("0.00")

        # --- Annual ---
        annual_targets = MonthlyTarget.objects.filter(user=user, year=current_year)
        annual_target = sum((t.target_amount for t in annual_targets), Decimal("0.00"))

        annual_opps = Opportunity.objects.filter(
            Q(lead__created_by=user) | Q(lead__assigned_to=user),
            closing_date__year=current_year,
            opportunity_status=34,
            is_active=True
        ).aggregate(total=Sum("opportunity_value"))
        annual_ach = Decimal(annual_opps["total"] or 0)

        last_year_opps = Opportunity.objects.filter(
            Q(lead__created_by=user) | Q(lead__assigned_to=user),
            closing_date__year=current_year - 1,
            is_active=True
        ).aggregate(total=Sum("opportunity_value"))
        last_year_ach = Decimal(last_year_opps["total"] or 0)

        # --- Build Response ---
        analytics_data = [
            {
                "type": "prevMonth",
                "title": "Previous Month",
                "subtitle": "Last month’s performance",
                "target": prev_target,
                "achieved": prev_ach,
                "percentage": pct(prev_ach, prev_target),
                "increase": prev_inc,
            },
            {
                "type": "currentMonth",
                "title": "Current Month",
                "subtitle": "Ongoing month’s progress",
                "target": curr_target,
                "achieved": curr_ach,
                "percentage": pct(curr_ach, curr_target),
                "increase": curr_inc,
            },
            {
                "type": "nextMonth",
                "title": "Next Month",
                "subtitle": "Upcoming target forecast",
                "target": next_target,
                "achieved": next_ach,
                "percentage": 0,
                "increase": False,
            },
            {
                "type": "annual",
                "title": "Annual Target",
                "subtitle": "Yearly summary",
                "target": annual_target,
                "achieved": annual_ach,
                "percentage": pct(annual_ach, annual_target),
                "increase": inc(annual_ach, last_year_ach),
            },
        ]

        serializer = TargetAnalyticsSerializer(analytics_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
