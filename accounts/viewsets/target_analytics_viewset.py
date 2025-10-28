from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from accounts.models import MonthlyTarget
from accounts.serializers.target_analytics_serializer import TargetAnalyticsSerializer
from lead.models import Opportunity
from django.contrib.auth import get_user_model

User = get_user_model()


class TargetAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='analytics')
    def get_analytics(self, request):
        user = request.user
        user_id = request.query_params.get("user_id")

        # --- Check if user belongs to Admin group ---
        is_admin = user.groups.filter(name__iexact="Admin").exists()

        # --- Determine which user's data to show ---
        if is_admin and user_id:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            target_user = user

        today = date.today()
        prev = today - relativedelta(months=1)
        next_m = today + relativedelta(months=1)

        # --- Helper Functions ---
        def get_target(month, year):
            val = MonthlyTarget.objects.filter(user=target_user, month=month, year=year).aggregate(total=Sum("target_amount"))["total"]
            return Decimal(val or 0)

        def get_achieved(month, year):
            val = Opportunity.objects.filter(
                Q(lead__created_by=target_user) | Q(lead__assigned_to=target_user),
                closing_date__month=month,
                closing_date__year=year,
                opportunity_status=34,
                is_active=True
            ).aggregate(total=Sum("opportunity_value"))["total"]
            return Decimal(val or 0)

        def pct(achieved, target):
            return int(round((achieved / target) * 100)) if target > 0 else 0

        def inc(curr, prev):
            return curr > prev

        # --- Monthly Data ---
        prev_target, prev_ach = get_target(prev.month, prev.year), get_achieved(prev.month, prev.year)
        curr_target, curr_ach = get_target(today.month, today.year), get_achieved(today.month, today.year)
        next_target = get_target(next_m.month, next_m.year)

        prev_inc = inc(prev_ach, get_achieved((today - relativedelta(months=2)).month, (today - relativedelta(months=2)).year))
        curr_inc = inc(curr_ach, prev_ach)

        # --- Annual Data ---
        annual_target = MonthlyTarget.objects.filter(user=target_user, year=today.year).aggregate(total=Sum("target_amount"))["total"] or Decimal(0)
        annual_ach = Opportunity.objects.filter(
            Q(lead__created_by=target_user) | Q(lead__assigned_to=target_user),
            closing_date__year=today.year,
            opportunity_status=34,
            is_active=True
        ).aggregate(total=Sum("opportunity_value"))["total"] or Decimal(0)

        # --- Build Response ---
        data = [
            {"type": "prevMonth", "title": "Previous Month", "target": prev_target, "achieved": prev_ach, "percentage": pct(prev_ach, prev_target), "increase": prev_inc},
            {"type": "currentMonth", "title": "Current Month", "target": curr_target, "achieved": curr_ach, "percentage": pct(curr_ach, curr_target), "increase": curr_inc},
            {"type": "nextMonth", "title": "Next Month", "target": next_target, "achieved": 0, "percentage": 0, "increase": False},
            {"type": "annual", "title": "Annual Target", "target": annual_target, "achieved": annual_ach, "percentage": pct(annual_ach, annual_target), "increase": inc(annual_ach, Decimal(0))}
        ]

        return Response(TargetAnalyticsSerializer(data, many=True).data, status=status.HTTP_200_OK)
