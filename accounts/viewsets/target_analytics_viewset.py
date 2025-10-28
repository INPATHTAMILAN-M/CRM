from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth import get_user_model

from accounts.models import MonthlyTarget, Teams
from accounts.serializers.target_analytics_serializer import TargetAnalyticsSerializer
from lead.models import Opportunity, Lead


class TargetAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for target analytics calculations."""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="analytics")
    def get_analytics(self, request):
        User = get_user_model()
        user = request.user
        is_admin = user.groups.filter(name__iexact="admin").exists()

        # --- Determine Target Users ---
        if is_admin:
            user_id = request.query_params.get("user_id")
            company_name = request.query_params.get("company_name")
            team_id = request.query_params.get("team_id")

            if user_id:
                target_users = User.objects.filter(id=user_id)
            elif team_id:
                team = Teams.objects.filter(id=team_id).first()
                if not team:
                    return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
                target_users = [team.bdm_user, *team.bde_user.all()]
            elif company_name:
                leads = Lead.objects.filter(name__icontains=company_name)
                user_ids = {l.created_by_id for l in leads if l.created_by_id} | {
                    l.assigned_to_id for l in leads if l.assigned_to_id
                }
                target_users = User.objects.filter(id__in=user_ids)
            else:
                target_users = User.objects.filter(is_active=True).exclude(groups__name__iexact="admin")
        else:
            target_users = [user]

        if not target_users:
            return Response({"error": "No matching users found."}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        prev_date, next_date = today - relativedelta(months=1), today + relativedelta(months=1)

        # --- Helper Functions ---
        def pct(achieved, target):
            if not target:
                return 0
            achieved, target = Decimal(str(achieved)), Decimal(str(target))
            return int(((achieved / target) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        def get_value(model, users, month=None, year=None):
            filters = Q()
            for u in users:
                filters |= Q(lead__created_by=u) | Q(lead__assigned_to=u)
            qs = model.objects.filter(filters, is_active=True)
            if month:
                qs = qs.filter(closing_date__month=month)
            if year:
                qs = qs.filter(closing_date__year=year)
            return Decimal(qs.aggregate(total=Sum("opportunity_value"))["total"] or 0)

        def get_target(month, year):
            return (
                MonthlyTarget.objects.filter(user__in=target_users, month=month, year=year)
                .aggregate(total=Sum("target_amount"))
                .get("total")
                or Decimal("0.00")
            )

        # --- Calculate Values ---
        prev_target = get_target(prev_date.month, prev_date.year)
        curr_target = get_target(today.month, today.year)
        next_target = get_target(next_date.month, next_date.year)

        prev_ach = get_value(Opportunity, target_users, prev_date.month, prev_date.year)
        curr_ach = get_value(Opportunity, target_users, today.month, today.year)
        annual_ach = get_value(Opportunity, target_users, year=today.year)
        last_year_ach = get_value(Opportunity, target_users, year=today.year - 1)

        annual_target = (
            MonthlyTarget.objects.filter(user__in=target_users, year=today.year)
            .aggregate(total=Sum("target_amount"))
            .get("total")
            or Decimal("0.00")
        )

        # --- Response ---
        data = [
            {
                "type": "prevMonth",
                "title": "Previous Month",
                "subtitle": "Last month’s performance",
                "target": prev_target,
                "achieved": prev_ach,
                "percentage": pct(prev_ach, prev_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "currentMonth",
                "title": "Current Month",
                "subtitle": "Ongoing month’s progress",
                "target": curr_target,
                "achieved": curr_ach,
                "percentage": pct(curr_ach, curr_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "nextMonth",
                "title": "Next Month",
                "subtitle": "Upcoming target forecast",
                "target": next_target,
                "achieved": Decimal("0.00"),
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
                "increase": annual_ach > last_year_ach,
            },
        ]

        return Response(TargetAnalyticsSerializer(data, many=True).data)
