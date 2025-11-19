# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from django.db.models import Q, Sum
# from datetime import date 
# from dateutil.relativedelta import relativedelta
# from decimal import Decimal, ROUND_HALF_UP
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
# from django.contrib.auth import get_user_model
# from accounts.models import MonthlyTarget, Teams
# from lead.models import Opportunity, Lead


# class TargetAnalyticsViewSet(viewsets.ViewSet):
#     """ViewSet for target analytics calculations."""
#     permission_classes = [IsAuthenticated]
#     @extend_schema(
#         parameters=[
#             OpenApiParameter(name='user_id', description='Filter by user id', required=False, type=OpenApiTypes.INT),
#             OpenApiParameter(name='team_id', description='Filter by team id', required=False, type=OpenApiTypes.INT),
#             OpenApiParameter(name='company_name', description='Filter by company name (lead name)', required=False, type=OpenApiTypes.STR),
#             OpenApiParameter(name='team', description='If true (with team_id): return BDE users of the given team; if true (with only user_id): return that user’s team BDEs; if false: only that user', required=False, type=OpenApiTypes.BOOL),
#         ]
#     )
#     @action(detail=False, methods=["get"], url_path="analytics")
#     def get_analytics(self, request):

#         # --- Proceed with analytics ---
#         today = date.today()
#         prev_date, next_date = today - relativedelta(months=1), today + relativedelta(months=1)

#         # --- Helper Functions ---
#         def pct(achieved, target):
#             if not target:
#                 return 0
#             achieved, target = Decimal(str(achieved)), Decimal(str(target))
#             return int(((achieved / target) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

#         # def get_value(model, users, month=None, year=None):
#         #     total_value = Decimal("0.00")

#         #     for target_user in users:
#         #         qs = model.objects.filter(opportunity_status=34, is_active=True)
#         #         if month:
#         #             qs = qs.filter(closing_date__month=month)
#         #         if year:
#         #             qs = qs.filter(closing_date__year=year)
#         #         filters_with_weights = [
#         #             (Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 1),
#         #             (Q(lead__created_by=target_user) & ~Q(lead__assigned_to=target_user), 0.5),
#         #             (~Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 0.5),
#         #             (Q(lead__created_by=target_user) & Q(lead__assigned_to__isnull=True), 1),
#         #         ]
#         #         for condition, weight in filters_with_weights:
#         #             value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
#         #             total_value += Decimal(value) * Decimal(weight)
#         #     return total_value
#         def get_value(model, users, month=None, year=None):
#             total_value = Decimal("0.00")

#             for target_user in users:
#                 qs = model.objects.filter(opportunity_status=34, is_active=True)
#                 if month:
#                     qs = qs.filter(closing_date__month=month)
#                 if year:
#                     qs = qs.filter(closing_date__year=year)
#                 # Make conditions mutually exclusive to avoid double counting.
#                 # 1) both roles -> full credit
#                 # 2) created_by and assigned_to is NULL -> full credit
#                 # 3) created_by and assigned_to present but assigned_to != user -> half credit
#                 # 4) assigned_to == user but created_by != user -> half credit
#                 filters_with_weights = [
#                     (Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 1),
#                     (Q(lead__created_by=target_user) & Q(lead__assigned_to__isnull=True), 1),
#                     (Q(lead__created_by=target_user) & ~Q(lead__assigned_to=target_user) & Q(lead__assigned_to__isnull=False), 0.5),
#                     (~Q(lead__created_by=target_user) & Q(lead__assigned_to=target_user), 0.5),
#                 ]
#                 for condition, weight in filters_with_weights:
#                     value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
#                     total_value += Decimal(value) * Decimal(weight)
#             return total_value
#         def get_target(month, year):
#             return (
#                 MonthlyTarget.objects.filter(user__in=target_users, month=month, year=year)
#                 .aggregate(total=Sum("target_amount"))
#                 .get("total")
#                 or Decimal("0.00")
#             )

#         def month_year_pairs(start_date, end_date):
#             pairs = []
#             cur = start_date.replace(day=1)
#             while cur <= end_date:
#                 pairs.append((cur.month, cur.year))
#                 cur = (cur + relativedelta(months=1)).replace(day=1)
#             return pairs

#         def sum_targets_for_range(start_date, end_date):
#             pairs = month_year_pairs(start_date, end_date)
#             total = Decimal("0.00")
#             for m, y in pairs:
#                 total += get_target(m, y)
#             return total

#         def sum_achieved_for_range(start_date, end_date):
#             pairs = month_year_pairs(start_date, end_date)
#             total = Decimal("0.00")
#             for m, y in pairs:
#                 total += get_value(Opportunity, target_users, month=m, year=y)
#             return total

#         team_flag = str(request.query_params.get("team", "")).lower() in ("true", "1", "yes")
#         user_id = request.query_params.get("user_id")

#         requester = request.user
#         User = get_user_model()

#         # Normalize roles
#         groups = {g.lower() for g in requester.groups.values_list('name', flat=True)}
#         is_admin = "admin" in groups
#         is_bdm = "bdm" in groups
#         is_bde = "bde" in groups   # optional in case needed for later

#         target_users = []

#         if not team_flag:
#             target_users = [requester]
#         else:
#             if is_admin:
#                 # Admin → All users except themselves
#                 target_users = list(User.objects.exclude(id=requester.id))

#             elif is_bdm:
#                 # BDM → All BDEs under their team
#                 team = Teams.objects.filter(bdm_user=requester).first()
#                 target_users = list(team.bde_user.all()) if team else []

#             else:
#                 # Others (BDE/normal users) → Only themselves
#                 target_users = [requester]

#         if user_id:
#             user_id = int(user_id)
#             target_users = [u for u in target_users if u.id == user_id]

#         target_users = target_users
        
#         print(f"DEBUG: target_users count={len(target_users)}")    
#         # --- Calculate Values ---
#         prev_target = get_target(prev_date.month, prev_date.year)
#         curr_target = get_target(today.month, today.year)
#         next_target = get_target(next_date.month, next_date.year)

#         # Financial Year (Apr - Mar)
#         fy_start_year = today.year if today.month >= 4 else today.year - 1
#         fy_start = date(fy_start_year, 4, 1)
#         fy_end = date(fy_start_year + 1, 3, 31)
#         financial_target = sum_targets_for_range(fy_start, fy_end)
#         financial_achieved = sum_achieved_for_range(fy_start, fy_end)

#         prev_fy_start = date(fy_start_year - 1, 4, 1)
#         prev_fy_end = date(fy_start_year, 3, 31)
#         prev_financial_achieved = sum_achieved_for_range(prev_fy_start, prev_fy_end)

#         prev_ach = get_value(Opportunity, target_users, prev_date.month, prev_date.year)
#         curr_ach = get_value(Opportunity, target_users, today.month, today.year)
#         annual_ach = get_value(Opportunity, target_users, year=today.year)
#         last_year_ach = get_value(Opportunity, target_users, year=today.year - 1)

#         annual_target = (
#             MonthlyTarget.objects.filter(user__in=target_users, year=today.year)
#             .aggregate(total=Sum("target_amount"))
#             .get("total")
#             or Decimal("0.00")
#         )

#         prev_month_start = prev_date.replace(day=1)
#         prev_month_end = today.replace(day=1) - relativedelta(days=1)
#         curr_month_start = today.replace(day=1)
#         curr_month_end = (today.replace(day=1) + relativedelta(months=1)) - relativedelta(days=1)
#         physical_year_start = date(today.year, 1, 1)
#         physical_year_end = date(today.year, 12, 31)

#         # --- Response ---
#         # Ensure decimals are quantized to match serializer's DecimalField
#         def quantize_decimal(value, places=2):
#             try:
#                 if value is None:
#                     return Decimal("0.00")
#                 dec = value if isinstance(value, Decimal) else Decimal(str(value))
#                 quantize_exp = Decimal(10) ** -places
#                 return dec.quantize(quantize_exp, rounding=ROUND_HALF_UP)
#             except Exception:
#                 return Decimal("0.00")

#         data = [
#             {
#                 "type": "prevMonth",
#                 "title": "Previous Month",
#                 "subtitle": "Last month's performance",
#                 "start_date": prev_month_start.strftime("%Y-%m-%d"),
#                 "end_date": prev_month_end.strftime("%Y-%m-%d"),
#                 "target": quantize_decimal(prev_target),
#                 "achieved": quantize_decimal(prev_ach),
#                 "percentage": pct(prev_ach, prev_target),
#                 "increase": curr_ach > prev_ach,
#             },
#             {
#                 "type": "currentMonth",
#                 "title": "Current Month",
#                 "subtitle": "Ongoing month's progress",
#                 "start_date": curr_month_start.strftime("%Y-%m-%d"),
#                 "end_date": curr_month_end.strftime("%Y-%m-%d"),
#                 "target": quantize_decimal(curr_target),
#                 "achieved": quantize_decimal(curr_ach),
#                 "percentage": pct(curr_ach, curr_target),
#                 "increase": curr_ach > prev_ach,
#             },
#             {
#                 "type": "financialYear",
#                 "title": "Financial Year",
#                 "subtitle": "Apr - Mar financial year",
#                 "start_date": fy_start.strftime("%Y-%m-%d"),
#                 "end_date": fy_end.strftime("%Y-%m-%d"),
#                 "target": quantize_decimal(financial_target),
#                 "achieved": quantize_decimal(financial_achieved),
#                 "percentage": pct(financial_achieved, financial_target),
#                 "increase": financial_achieved > prev_financial_achieved,
#             },
#             {
#                 "type": "PhysicalYear",
#                 "title": "Physical Year",
#                 "subtitle": "Yearly summary",
#                 "start_date": physical_year_start.strftime("%Y-%m-%d"),
#                 "end_date": physical_year_end.strftime("%Y-%m-%d"),
#                 "target": quantize_decimal(annual_target),
#                 "achieved": quantize_decimal(annual_ach),
#                 "percentage": pct(annual_ach, annual_target),
#                 "increase": annual_ach > last_year_ach,
#             },
#         ]

#         # Convert Decimal values to strings (preserve exactness) instead of floats
#         out_data = []
#         for item in data:
#             new_item = item.copy()
#             for key in ("target", "achieved"):
#                 val = new_item.get(key)
#                 try:
#                     if isinstance(val, Decimal):
#                         # Format as string with 2 decimal places
#                         new_item[key] = str(val.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
#                     else:
#                         new_item[key] = str(Decimal(str(val)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))
#                 except Exception:
#                     # fallback to "0.00" for any unconvertible values
#                     new_item[key] = "0.00"
#             out_data.append(new_item)

#         return Response(out_data)


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.contrib.auth import get_user_model
from accounts.models import MonthlyTarget, Teams
from lead.models import Opportunity


class TargetAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='Filter by user id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='team_id', description='Filter by team id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='company_name', description='Filter by company name', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='team', description='If true: include team users', required=False, type=OpenApiTypes.BOOL),
        ]
    )
    @action(detail=False, methods=["get"], url_path="analytics")
    def get_analytics(self, request):

        today = date.today()
        prev_date, next_date = today - relativedelta(months=1), today + relativedelta(months=1)

        # Percentage calculation
        def pct(achieved, target):
            if not target:
                return 0
            achieved, target = Decimal(str(achieved)), Decimal(str(target))
            return int(((achieved / target) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        # Weighted achievement calculation
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
                    (Q(lead__created_by=target_user) & Q(lead__assigned_to__isnull=True), 1),
                    (Q(lead__created_by=target_user) & ~Q(lead__assigned_to=target_user) & Q(lead__assigned_to__isnull=False), 0.5),
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

        # Date helpers
        def month_year_pairs(start_date, end_date):
            pairs = []
            cur = start_date.replace(day=1)
            while cur <= end_date:
                pairs.append((cur.month, cur.year))
                cur = (cur + relativedelta(months=1)).replace(day=1)
            return pairs

        def sum_targets_for_range(start_date, end_date):
            total = Decimal("0.00")
            for m, y in month_year_pairs(start_date, end_date):
                total += get_target(m, y)
            return total

        def sum_achieved_for_range(start_date, end_date):
            total = Decimal("0.00")
            for m, y in month_year_pairs(start_date, end_date):
                total += get_value(Opportunity, target_users, month=m, year=y)
            return total

        User = get_user_model()

        requester = request.user
        groups = {g.lower() for g in requester.groups.values_list("name", flat=True)}

        is_admin = "admin" in groups
        is_bdm = "bdm" in groups

        team_flag = str(request.query_params.get("team", "")).lower() in ("true", "1", "yes")
        user_id = request.query_params.get("user_id")

        target_users = []

        # Normal flow
        if not team_flag:
            target_users = [requester]
        else:
            if is_admin:
                target_users = list(User.objects.exclude(id=requester.id))
            elif is_bdm:
                team = Teams.objects.filter(bdm_user=requester).first()
                target_users = list(team.bde_user.all()) if team else []
            else:
                target_users = [requester]

        # 🔥 FIX: user_id supports TM / DM / ANY user including those not in Teams table
        if user_id:
            try:
                target_users = [User.objects.get(id=int(user_id))]
            except User.DoesNotExist:
                target_users = []

        # ---- Calculate Values ----
        prev_target = get_target(prev_date.month, prev_date.year)
        curr_target = get_target(today.month, today.year)
        next_target = get_target(next_date.month, next_date.year)

        # FY (Apr–Mar)
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

        def quantize_decimal(value):
            if value is None:
                return "0.00"
            return str(Decimal(value).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP))

        output = [
            {
                "type": "prevMonth",
                "title": "Previous Month",
                "start_date": str(prev_month_start),
                "end_date": str(prev_month_end),
                "target": quantize_decimal(prev_target),
                "achieved": quantize_decimal(prev_ach),
                "percentage": pct(prev_ach, prev_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "currentMonth",
                "title": "Current Month",
                "start_date": str(curr_month_start),
                "end_date": str(curr_month_end),
                "target": quantize_decimal(curr_target),
                "achieved": quantize_decimal(curr_ach),
                "percentage": pct(curr_ach, curr_target),
                "increase": curr_ach > prev_ach,
            },
            {
                "type": "financialYear",
                "title": "Financial Year",
                "start_date": str(fy_start),
                "end_date": str(fy_end),
                "target": quantize_decimal(financial_target),
                "achieved": quantize_decimal(financial_achieved),
                "percentage": pct(financial_achieved, financial_target),
                "increase": financial_achieved > prev_financial_achieved,
            },
            {
                "type": "PhysicalYear",
                "title": "Physical Year",
                "start_date": str(physical_year_start),
                "end_date": str(physical_year_end),
                "target": quantize_decimal(annual_target),
                "achieved": quantize_decimal(annual_ach),
                "percentage": pct(annual_ach, annual_target),
                "increase": annual_ach > last_year_ach,
            },
        ]

        return Response(output)
