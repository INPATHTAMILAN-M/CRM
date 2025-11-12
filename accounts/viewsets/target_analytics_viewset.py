from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from accounts.models import MonthlyTarget, Teams
# Serializer not used for output anymore because we return primitive types
from lead.models import Opportunity, Lead


class TargetAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for target analytics calculations."""
    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='Filter by user id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='team_id', description='Filter by team id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='company_name', description='Filter by company name (lead name)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='team', description='If true (with team_id): return BDE users of the given team; if true (with only user_id): return that user’s team BDEs; if false: only that user', required=False, type=OpenApiTypes.BOOL),
        ]
    )
    @action(detail=False, methods=["get"], url_path="analytics")
    def get_analytics(self, request):
        User = get_user_model()
        user = request.user

        # --- Parse query params ---
        team_param = request.query_params.get("team")
        team_flag = False
        if team_param is not None:
            try:
                team_flag = str(team_param).strip().lower() in ("1", "true", "yes")
            except Exception:
                team_flag = False

        team_id = request.query_params.get("team_id")
        user_id = request.query_params.get("user_id")
        # --- Determine Target Users ---
        # Role-based access rules:
        # - admin (is_superuser): can view all users/teams; if no filters provided, return all users
        # - BDM: can view their team (BDM + all BDEs)
        # - BDE: can view only themselves
        target_users = []

        # helper to load user object from user_id param
        def load_user_by_id(uid):
            try:
                uid = int(uid)
            except (TypeError, ValueError):
                return None
            return User.objects.filter(id=uid).first()

        # Detect if request.user is a BDM (has a Teams entry as bdm_user)
        user_team = Teams.objects.filter(bdm_user=user).first()
        is_bdm = bool(user_team)
        is_admin = getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)

        # If caller is admin, allow broad access
        if is_admin:
            if team_flag:
                if team_id:
                    team = Teams.objects.filter(id=team_id).first()
                    if not team:
                        return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
                    target_users = list(team.bde_user.all()) + ([team.bdm_user] if getattr(team, 'bdm_user', None) else [])
                elif user_id:
                    user_obj = load_user_by_id(user_id)
                    if user_obj:
                        # If the supplied user belongs to a team, include that team's BDEs
                        ut = Teams.objects.filter(Q(bde_user=user_obj) | Q(bdm_user=user_obj)).first()
                        if ut:
                            target_users = list(ut.bde_user.all()) + ([ut.bdm_user] if getattr(ut, 'bdm_user', None) else [])
                        else:
                            target_users = [user_obj]
                    else:
                        target_users = []
                else:
                    # admin + team_flag but no specific team/user -> all users
                    target_users = list(User.objects.all())
            else:
                if user_id:
                    user_obj = load_user_by_id(user_id)
                    target_users = [user_obj] if user_obj else []
                else:
                    # admin default -> all users
                    target_users = list(User.objects.all())

        # If caller is BDM, restrict to their team (BDM + all BDEs). If user_id provided, allow drilling into specific user
        elif is_bdm:
            if team_flag and team_id:
                team = Teams.objects.filter(id=team_id).first()
                if not team:
                    return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
                target_users = list(team.bde_user.all()) + ([team.bdm_user] if getattr(team, 'bdm_user', None) else [])
            else:
                # default to the BDM's own team
                target_users = list(user_team.bde_user.all()) + ([user_team.bdm_user] if getattr(user_team, 'bdm_user', None) else [])
                if user_id:
                    # If they asked for a particular user in their team, narrow to that user
                    user_obj = load_user_by_id(user_id)
                    if user_obj and (user_obj in target_users):
                        target_users = [user_obj]

        # Otherwise treat as BDE or normal user: only themselves (unless admin filtered)
        else:
            if user_id:
                user_obj = load_user_by_id(user_id)
                # only allow viewing self
                if user_obj and user_obj.id == user.id:
                    target_users = [user_obj]
                else:
                    target_users = [user]
            else:
                target_users = [user]

        # de-duplicate users
        # ensure we have actual user instances
        target_users = [u for i, u in enumerate(target_users) if u and u not in target_users[:i]]

        # --- Proceed with analytics ---
        today = date.today()
        prev_date, next_date = today - relativedelta(months=1), today + relativedelta(months=1)

        # --- Helper Functions ---
        def pct(achieved, target):
            if not target:
                return 0
            achieved, target = Decimal(str(achieved)), Decimal(str(target))
            return int(((achieved / target) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        def get_value(model, users, month=None, year=None):
            total_value = Decimal("0.00")

            for target_user in users:
                qs = model.objects.filter(opportunity_status=34, is_active=True)
                if month:
                    qs = qs.filter(closing_date__month=month)
                if year:
                    qs = qs.filter(closing_date__year=year)
                filters_with_weights = [
                    (Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 1),
                    (Q(lead__created_by=target_user) & ~Q(lead__assigned_to=target_user), 0.5),
                    (~Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 0.5),
                ]
                for condition, weight in filters_with_weights:
                    value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
                    total_value += Decimal(value) * Decimal(weight)
            return total_value

        def get_target(month, year):
            return (
                MonthlyTarget.objects.filter(user__in=target_users, month=month, year=year)
                .aggregate(total=Sum("target_amount"))
                .get("total")
                or Decimal("0.00")
            )

        def month_year_pairs(start_date, end_date):
            pairs = []
            cur = start_date.replace(day=1)
            while cur <= end_date:
                pairs.append((cur.month, cur.year))
                cur = (cur + relativedelta(months=1)).replace(day=1)
            return pairs

        def sum_targets_for_range(start_date, end_date):
            pairs = month_year_pairs(start_date, end_date)
            total = Decimal("0.00")
            for m, y in pairs:
                total += get_target(m, y)
            return total

        def sum_achieved_for_range(start_date, end_date):
            pairs = month_year_pairs(start_date, end_date)
            total = Decimal("0.00")
            for m, y in pairs:
                total += get_value(Opportunity, target_users, month=m, year=y)
            return total

        # --- Calculate Values ---
        prev_target = get_target(prev_date.month, prev_date.year)
        curr_target = get_target(today.month, today.year)
        next_target = get_target(next_date.month, next_date.year)

        # Financial Year (Apr - Mar)
        fy_start_year = today.year if today.month >= 4 else today.year - 1
        fy_start = date(fy_start_year, 4, 1)
        fy_end = date(fy_start_year + 1, 3, 31)
        financial_target = sum_targets_for_range(fy_start, fy_end)
        financial_achieved = sum_achieved_for_range(fy_start, fy_end)

        prev_fy_start = date(fy_start_year - 1, 4, 1)
        prev_fy_end = date(fy_start_year, 3, 31)
        prev_financial_achieved = sum_achieved_for_range(prev_fy_start, prev_fy_end)

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

        prev_month_start = prev_date.replace(day=1)
        prev_month_end = today.replace(day=1) - relativedelta(days=1)
        curr_month_start = today.replace(day=1)
        curr_month_end = (today.replace(day=1) + relativedelta(months=1)) - relativedelta(days=1)
        physical_year_start = date(today.year, 1, 1)
        physical_year_end = date(today.year, 12, 31)

        # --- Response ---
        # Ensure decimals are quantized to match serializer's DecimalField
        def quantize_decimal(value, places=2):
            try:
                if value is None:
                    return Decimal("0.00")
                dec = value if isinstance(value, Decimal) else Decimal(str(value))
                quantize_exp = Decimal(10) ** -places
                return dec.quantize(quantize_exp, rounding=ROUND_HALF_UP)
            except Exception:
                return Decimal("0.00")

        data = [
            {
                "type": "prevMonth",
                "title": "Previous Month",
                "subtitle": "Last month's performance",
                "start_date": prev_month_start.strftime("%Y-%m-%d"),
                "end_date": prev_month_end.strftime("%Y-%m-%d"),
                "target": quantize_decimal(prev_target),
                "achieved": quantize_decimal(prev_ach),
                "percentage": pct(prev_ach, prev_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "currentMonth",
                "title": "Current Month",
                "subtitle": "Ongoing month's progress",
                "start_date": curr_month_start.strftime("%Y-%m-%d"),
                "end_date": curr_month_end.strftime("%Y-%m-%d"),
                "target": quantize_decimal(curr_target),
                "achieved": quantize_decimal(curr_ach),
                "percentage": pct(curr_ach, curr_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "financialYear",
                "title": "Financial Year",
                "subtitle": "Apr - Mar financial year",
                "start_date": fy_start.strftime("%Y-%m-%d"),
                "end_date": fy_end.strftime("%Y-%m-%d"),
                "target": quantize_decimal(financial_target),
                "achieved": quantize_decimal(financial_achieved),
                "percentage": pct(financial_achieved, financial_target),
                "increase": financial_achieved > prev_financial_achieved,
            },
            {
                "type": "PhysicalYear",
                "title": "Physical Year",
                "subtitle": "Yearly summary",
                "start_date": physical_year_start.strftime("%Y-%m-%d"),
                "end_date": physical_year_end.strftime("%Y-%m-%d"),
                "target": quantize_decimal(annual_target),
                "achieved": quantize_decimal(annual_ach),
                "percentage": pct(annual_ach, annual_target),
                "increase": annual_ach > last_year_ach,
            },
        ]

        # Convert Decimal values to native types (floats) to avoid DecimalField quantize errors
        out_data = []
        for item in data:
            new_item = item.copy()
            for key in ("target", "achieved"):
                val = new_item.get(key)
                try:
                    if isinstance(val, Decimal):
                        new_item[key] = float(val)
                    else:
                        new_item[key] = float(Decimal(str(val)))
                except Exception:
                    # fallback to 0.0 for any unconvertible values
                    new_item[key] = 0.0
            out_data.append(new_item)

        return Response(out_data)
