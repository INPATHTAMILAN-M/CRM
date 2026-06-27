# from datetime import date
# from decimal import Decimal, ROUND_HALF_UP
# from dateutil.relativedelta import relativedelta
# from django.db.models import Q, Sum
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

# from accounts.models import MonthlyTarget, Teams
# from accounts.models import UserActiveHistory
# from lead.models import Opportunity, Lead


# class AnnualTargetAnalyticsViewSet(viewsets.ViewSet):
#     """
#     Returns annual analytics (financial Apr–Mar or physical Jan–Dec).
#     Supports summary (current period) or detailed (all periods).
#     """
#     permission_classes = [IsAuthenticated]

#     def _get_target_users(self, request):
#         User = get_user_model()
#         user = request.user
#         is_admin = user.groups.filter(name__iexact="admin").exists()

#         user_id = request.query_params.get("user_id")
#         team_id = request.query_params.get("team_id")
#         company_name = request.query_params.get("company_name")
#         team_flag = request.query_params.get("team", "").lower() == "true"

#         # Admin can query any user, team, or company
#         if is_admin:
#             if user_id:
#                 return User.objects.filter(id=user_id)

#             if team_id:
#                 team = Teams.objects.filter(id=team_id).first()
#                 if not team:
#                     return None
#                 return [team.bdm_user, *team.bde_user.all()]

#             if company_name:
#                 leads = Lead.objects.filter(name__icontains=company_name)
#                 user_ids = {l.created_by_id for l in leads if l.created_by_id} | {
#                     l.assigned_to_id for l in leads if l.assigned_to_id
#                 }
#                 return User.objects.filter(id__in=user_ids)

#             if team_flag:
#                 return User.objects.exclude(id=user.id)

#             return User.objects.filter(is_active=True).exclude(groups__name__iexact="admin")

#         # Non-admin (BDM/BDE): can only query their own data or their team's data
        
#         # Handle team=true: return BDM's team members (excluding BDM themselves)
#         if team_flag:
#             bdm_team = Teams.objects.filter(bdm_user=user).first()
#             if bdm_team:
#                 # Return only the BDE team members, not the BDM
#                 return list(bdm_team.bde_user.all())
#             return User.objects.none()

#         # If user_id is provided, check if it's their own or a team member
#         if user_id:
#             target_user = User.objects.filter(id=user_id).first()
#             if not target_user:
#                 return User.objects.none()

#             # Allow if it's their own id or they're a BDM with the target user in their team
#             if target_user.id == user.id:
#                 return [target_user]

#             # Check if user is a BDM and target_user is in their team
#             bdm_team = Teams.objects.filter(bdm_user=user).first()
#             if bdm_team and target_user in bdm_team.bde_user.all():
#                 return [target_user]

#             # Not allowed
#             return User.objects.none()

#         # If team_id is provided, allow BDM to query their own team
#         if team_id:
#             team = Teams.objects.filter(id=team_id).first()
#             if not team:
#                 return None

#             # Allow if user is the BDM or a member of this team
#             if team.bdm_user.id == user.id:
#                 return [team.bdm_user, *team.bde_user.all()]

#             if team.bde_user.filter(id=user.id).exists():
#                 return [team.bdm_user, *team.bde_user.all()]

#             # Not allowed
#             return User.objects.none()

#         # If company_name is provided, only allow if user created/assigned to those leads
#         if company_name:
#             leads = Lead.objects.filter(
#                 name__icontains=company_name
#             ).filter(
#                 Q(created_by=user) | Q(assigned_to=user)
#             )
#             user_ids = {l.created_by_id for l in leads if l.created_by_id} | {
#                 l.assigned_to_id for l in leads if l.assigned_to_id
#             }
#             return User.objects.filter(id__in=user_ids) if user_ids else User.objects.none()

#         # Default: return own user
#         return [user]


#     def _month_year_gte(self, month, year, start_month, start_year):
#         return year > start_year or (year == start_year and month >= start_month)

#     def _month_year_lte(self, month, year, end_month, end_year):
#         return year < end_year or (year == end_year and month <= end_month)

#     def _month_year_in_range(self, month, year, start, end=None, inclusive_end=True):
#         if not self._month_year_gte(month, year, start.month, start.year):
#             return False
#         if end is None:
#             return True
#         if inclusive_end:
#             return self._month_year_lte(month, year, end.month, end.year)
#         return year < end.year or (year == end.year and month < end.month)

#     def _month_year_allowed(self, user, month, year):
#         histories = list(UserActiveHistory.objects.filter(user=user).order_by('changed_at'))

#         # If there are history changes within the requested month, use the
#         # latest change in that month to determine active state for that
#         # month (handles deactivate->reactivate within same month).
#         month_histories = [h for h in histories if h.changed_at.year == year and h.changed_at.month == month]
#         if month_histories:
#             return bool(month_histories[-1].is_active)

#         if not histories:
#             # If there's no recorded history, rely on the current `is_active` flag.
#             # - active users: allow months
#             # - inactive users: allow months up to now (safe backward-compat)
#             if user.is_active:
#                 return True
#             now = timezone.now()
#             return self._month_year_lte(month, year, now.month, now.year)

#         active_start = None

#         # If first history is inactive, assume user was active from date_joined until then
#         if histories and not histories[0].is_active and user.date_joined:
#             active_start = user.date_joined
#             if self._month_year_in_range(month, year, active_start, histories[0].changed_at, inclusive_end=False):
#                 return True
#             active_start = None

#         for h in histories:
#             if h.is_active:
#                 if active_start is None:
#                     active_start = h.changed_at
#                     if h == histories[0] and user.date_joined and user.date_joined < active_start:
#                         active_start = user.date_joined
#             else:
#                 if active_start is not None:
#                     if self._month_year_in_range(month, year, active_start, h.changed_at, inclusive_end=False):
#                         return True
#                     active_start = None

#         if active_start is not None:
#             if user.is_active:
#                 return self._month_year_in_range(month, year, active_start)
#             return self._month_year_in_range(month, year, active_start, timezone.now(), inclusive_end=False)

#         if user.is_active:
#             return self._month_year_in_range(month, year, timezone.now())

#         return False

#     def _sum_targets(self, users, start, end):
#         total = Decimal("0.00")
#         cur = start.replace(day=1)
#         while cur <= end:
#             for u in users:
#                 if not self._month_year_allowed(u, cur.month, cur.year):
#                     continue
#                 value = MonthlyTarget.objects.filter(
#                     user=u,
#                     month=cur.month,
#                     year=cur.year,
#                 ).aggregate(total=Sum("target_amount"))["total"]
#                 total += Decimal(value or 0)
#             cur = (cur + relativedelta(months=1)).replace(day=1)
#         return total

#     def _sum_achieved(self, users, start, end):
#         total = Decimal("0.00")
#         cur = start.replace(day=1)
#         while cur <= end:
#             month_start = cur
#             month_end = (cur + relativedelta(months=1)) - relativedelta(days=1)
#             for u in users:
#                 if not self._month_year_allowed(u, cur.month, cur.year):
#                     continue

#                 qs = Opportunity.objects.filter(
#                     opportunity_status=34,
#                     is_active=True,
#                     closing_date__range=(month_start, month_end),
#                 )

#                 filters_with_weights = [
#                     (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
#                     (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
#                     (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
#                     (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
#                 ]

#                 for condition, weight in filters_with_weights:
#                     value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
#                     total += Decimal(value) * Decimal(weight)
#             cur = (cur + relativedelta(months=1)).replace(day=1)
#         return total

#     def _get_ranges(self, year_type, year):
#         if year_type == "financial":
#             start = date(year, 4, 1)
#             end = date(year + 1, 3, 31)
#         else:
#             start = date(year, 1, 1)
#             end = date(year, 12, 31)

#         return {
#             "monthly": [
#                 (start + relativedelta(months=i),
#                  (start + relativedelta(months=i + 1)) - relativedelta(days=1))
#                 for i in range(12)
#             ],
#             "quarterly": [
#                 (start + relativedelta(months=3 * i),
#                  (start + relativedelta(months=3 * (i + 1))) - relativedelta(days=1))
#                 for i in range(4)
#             ],
#             "half": [
#                 (start, start + relativedelta(months=6) - relativedelta(days=1)),
#                 (start + relativedelta(months=6), end),
#             ],
#             "annual": [(start, end)],
#         }


#     @extend_schema(
#         parameters=[
#             OpenApiParameter("year_type", description="'financial' or 'physical'", type=OpenApiTypes.STR),
#             OpenApiParameter("period", description="'monthly'|'quarterly'|'half'|'annual'|'all'", type=OpenApiTypes.STR),
#             OpenApiParameter("year", description="Year (e.g. 2024 for Apr-2024..Mar-2025)", type=OpenApiTypes.INT),
#             OpenApiParameter("user_id", description="User ID", type=OpenApiTypes.INT),
#             OpenApiParameter("team_id", description="Team ID", type=OpenApiTypes.INT),
#             OpenApiParameter("company_name", description="Company/Lead Name", type=OpenApiTypes.STR),
#             OpenApiParameter("summary", description="true/false — Return only summary view", type=OpenApiTypes.BOOL),
#         ]
#     )
#     @action(detail=False, methods=["get"], url_path="annual-analytics")
#     def annual_analytics(self, request):
#         year_type = request.query_params.get("year_type", "physical").lower()
#         period = request.query_params.get("period", "all").lower()
#         summary = request.query_params.get("summary", "false").lower() == "true"

#         try:
#             year = int(request.query_params.get("year", date.today().year))
#         except ValueError:
#             return Response({"error": "Invalid year"}, status=status.HTTP_400_BAD_REQUEST)

#         users = self._get_target_users(request)
#         if not users:
#             return Response({"error": "No matching users"}, status=status.HTTP_404_NOT_FOUND)

#         if summary:
#             today = date.today()
#             ranges = self._get_ranges(year_type, year)
#             titles = {"monthly": "monthly", "quarterly": "quarterly", "half": "half yearly", "annual": "annually"}
#             summary_data = []
            
#             for key in ["monthly", "quarterly", "half", "annual"]:
#                 # Find the current period that contains today's date
#                 current_range = None
#                 for start, end in ranges[key]:
#                     if start <= today <= end:
#                         current_range = (start, end)
#                         break
                
#                 # If no current range found, use the first one as fallback
#                 if not current_range:
#                     current_range = ranges[key][0] if ranges[key] else (today, today)
                
#                 start, end = current_range
#                 target = self._sum_targets(users, start, end)
#                 achieved = self._sum_achieved(users, start, end)
#                 pct = int(((achieved / target) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) if target else 0
#                 summary_data.append({
#                     "title": titles[key],
#                     "start_date": start.strftime("%Y-%m-%d"),
#                     "end_date": end.strftime("%Y-%m-%d"),
#                     "target": float(target),
#                     "achieved": float(achieved),
#                     "percentage": pct,
#                     "increase": pct > 50,
#                 })
#             return Response(summary_data)

#         # -------------------------
#         # DETAILED MODE
#         # -------------------------
#         ranges = self._get_ranges(year_type, year)
#         requested = [period] if period != "all" else ranges.keys()
#         results = []

#         for p in requested:
#             data = []
#             for start, end in ranges[p]:
#                 target = self._sum_targets(users, start, end)
#                 achieved = self._sum_achieved(users, start, end)
#                 pct = int(((achieved / target) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) if target else 0
#                 data.append({
#                     "label": f"{p.title()} {start.strftime('%b %Y')} - {end.strftime('%b %Y')}",
#                     "start": start,
#                     "end": end,
#                     "target": float(target),
#                     "achieved": float(achieved),
#                     "percentage": pct,
#                 })
#             results.append({"period_type": p, "items": data})
#         return Response(results)



from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from accounts.models import MonthlyTarget, Teams
from accounts.models import UserActiveHistory
from lead.models import Opportunity, Lead


class AnnualTargetAnalyticsViewSet(viewsets.ViewSet):
    """
    Returns annual analytics (financial Apr–Mar or physical Jan–Dec).
    Supports summary (current period) or detailed (all periods).
    """
    permission_classes = [IsAuthenticated]

    def _get_target_users(self, request):
        User = get_user_model()
        user = request.user
        is_admin = user.groups.filter(name__iexact="admin").exists()

        user_id = request.query_params.get("user_id")
        team_id = request.query_params.get("team_id")
        company_name = request.query_params.get("company_name")
        team_flag = request.query_params.get("team", "").lower() == "true"

        # Admin can query any user, team, or company
        if is_admin:
            if user_id:
                return User.objects.filter(id=user_id)

            if team_id:
                team = Teams.objects.filter(id=team_id).first()
                if not team:
                    return None
                return [team.bdm_user, *team.bde_user.all()]

            if company_name:
                leads = Lead.objects.filter(name__icontains=company_name)
                user_ids = {l.created_by_id for l in leads if l.created_by_id} | {
                    l.assigned_to_id for l in leads if l.assigned_to_id
                }
                return User.objects.filter(id__in=user_ids)

            if team_flag:
                return User.objects.exclude(id=user.id)

            return User.objects.filter(is_active=True).exclude(groups_name_iexact="admin")

        # Non-admin (BDM/BDE): can only query their own data or their team's data
        
        # Handle team=true: return BDM's team members (excluding BDM themselves)
        if team_flag:
            bdm_team = Teams.objects.filter(bdm_user=user).first()
            if bdm_team:
                # Return only the BDE team members, not the BDM
                return list(bdm_team.bde_user.all())
            return User.objects.none()

        # If user_id is provided, check if it's their own or a team member
        if user_id:
            target_user = User.objects.filter(id=user_id).first()
            if not target_user:
                return User.objects.none()

            # Allow if it's their own id or they're a BDM with the target user in their team
            if target_user.id == user.id:
                return [target_user]

            # Check if user is a BDM and target_user is in their team
            bdm_team = Teams.objects.filter(bdm_user=user).first()
            if bdm_team and target_user in bdm_team.bde_user.all():
                return [target_user]

            # Not allowed
            return User.objects.none()

        # If team_id is provided, allow BDM to query their own team
        if team_id:
            team = Teams.objects.filter(id=team_id).first()
            if not team:
                return None

            # Allow if user is the BDM or a member of this team
            if team.bdm_user.id == user.id:
                return [team.bdm_user, *team.bde_user.all()]

            if team.bde_user.filter(id=user.id).exists():
                return [team.bdm_user, *team.bde_user.all()]

            # Not allowed
            return User.objects.none()

        # If company_name is provided, only allow if user created/assigned to those leads
        if company_name:
            leads = Lead.objects.filter(
                name__icontains=company_name
            ).filter(
                Q(created_by=user) | Q(assigned_to=user)
            )
            user_ids = {l.created_by_id for l in leads if l.created_by_id} | {
                l.assigned_to_id for l in leads if l.assigned_to_id
            }
            return User.objects.filter(id__in=user_ids) if user_ids else User.objects.none()

        # Default: return own user
        return [user]


    def _month_year_gte(self, month, year, start_month, start_year):
        return year > start_year or (year == start_year and month >= start_month)

    def _month_year_lte(self, month, year, end_month, end_year):
        return year < end_year or (year == end_year and month <= end_month)

    def _month_year_in_range(self, month, year, start, end=None, inclusive_end=True):
        if not self._month_year_gte(month, year, start.month, start.year):
            return False
        if end is None:
            return True
        if inclusive_end:
            return self._month_year_lte(month, year, end.month, end.year)
        return year < end.year or (year == end.year and month < end.month)

    def _month_year_allowed(self, user, month, year):
        histories = list(UserActiveHistory.objects.filter(user=user).order_by('changed_at'))

        # If there are history changes within the requested month, use the
        # latest change in that month to determine active state for that
        # month (handles deactivate->reactivate within same month).
        month_histories = [h for h in histories if h.changed_at.year == year and h.changed_at.month == month]
        if month_histories:
            return bool(month_histories[-1].is_active)

        if not histories:
            # If there's no recorded history, rely on the current is_active flag.
            # - active users: allow months
            # - inactive users: allow months up to now (safe backward-compat)
            if user.is_active:
                return True
            now = timezone.now()
            return self._month_year_lte(month, year, now.month, now.year)

        active_start = None

        # If first history is inactive, assume user was active from date_joined until then
        if histories and not histories[0].is_active and user.date_joined:
            active_start = user.date_joined
            if self._month_year_in_range(month, year, active_start, histories[0].changed_at, inclusive_end=False):
                return True
            active_start = None

        for h in histories:
            if h.is_active:
                if active_start is None:
                    active_start = h.changed_at
                    if h == histories[0] and user.date_joined and user.date_joined < active_start:
                        active_start = user.date_joined
            else:
                if active_start is not None:
                    if self._month_year_in_range(month, year, active_start, h.changed_at, inclusive_end=False):
                        return True
                    active_start = None

        if active_start is not None:
            if user.is_active:
                return self._month_year_in_range(month, year, active_start)
            return self._month_year_in_range(month, year, active_start, timezone.now(), inclusive_end=False)

        if user.is_active:
            return self._month_year_in_range(month, year, timezone.now())

        return False

    def _sum_targets(self, users, start, end):
        """
        target_amount is a cumulative running total.
        Range target = the raw cumulative value at the LAST ALLOWED month
        within the range. Inactive users are capped at their last active month.
        """
        from django.db.models import Q as DQ
        total = Decimal("0.00")

        # Build month pairs for the range
        month_pairs = []
        cur = start.replace(day=1)
        while cur <= end:
            month_pairs.append((cur.month, cur.year))
            cur = (cur + relativedelta(months=1)).replace(day=1)

        for u in users:
            # Find the last month in the range where the user was allowed
            last_allowed = None
            for m, y in month_pairs:
                if self._month_year_allowed(u, m, y):
                    last_allowed = (m, y)
            if last_allowed is None:
                continue

            # Raw cumulative at last allowed month
            mt = MonthlyTarget.objects.filter(user=u).filter(
                DQ(year__lt=last_allowed[1]) | DQ(year=last_allowed[1], month__lte=last_allowed[0])
            ).order_by('-year', '-month').first()
            if mt:
                total += Decimal(mt.target_amount)

        return total

    def _sum_achieved(self, users, start, end):
        total = Decimal("0.00")
        cur = start.replace(day=1)
        while cur <= end:
            month_start = cur
            month_end = (cur + relativedelta(months=1)) - relativedelta(days=1)
            for u in users:
                if not self._month_year_allowed(u, cur.month, cur.year):
                    continue

                qs = Opportunity.objects.filter(
                    opportunity_status=34,
                    is_active=True,
                    closing_date__range=(month_start, month_end),
                )

                filters_with_weights = [
                    (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
                    (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
                    (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
                    (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
                ]

                for condition, weight in filters_with_weights:
                    value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
                    total += Decimal(value) * Decimal(weight)
            cur = (cur + relativedelta(months=1)).replace(day=1)
        return total

    def _get_ranges(self, year_type, year):
        if year_type == "financial":
            start = date(year, 4, 1)
            end = date(year + 1, 3, 31)
        else:
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        return {
            "monthly": [
                (start + relativedelta(months=i),
                 (start + relativedelta(months=i + 1)) - relativedelta(days=1))
                for i in range(12)
            ],
            "quarterly": [
                (start + relativedelta(months=3 * i),
                 (start + relativedelta(months=3 * (i + 1))) - relativedelta(days=1))
                for i in range(4)
            ],
            "half": [
                (start, start + relativedelta(months=6) - relativedelta(days=1)),
                (start + relativedelta(months=6), end),
            ],
            "annual": [(start, end)],
        }


    @extend_schema(
        parameters=[
            OpenApiParameter("year_type", description="'financial' or 'physical'", type=OpenApiTypes.STR),
            OpenApiParameter("period", description="'monthly'|'quarterly'|'half'|'annual'|'all'", type=OpenApiTypes.STR),
            OpenApiParameter("year", description="Year (e.g. 2024 for Apr-2024..Mar-2025)", type=OpenApiTypes.INT),
            OpenApiParameter("user_id", description="User ID", type=OpenApiTypes.INT),
            OpenApiParameter("team_id", description="Team ID", type=OpenApiTypes.INT),
            OpenApiParameter("company_name", description="Company/Lead Name", type=OpenApiTypes.STR),
            OpenApiParameter("summary", description="true/false — Return only summary view", type=OpenApiTypes.BOOL),
        ]
    )
    @action(detail=False, methods=["get"], url_path="annual-analytics")
    def annual_analytics(self, request):
        year_type = request.query_params.get("year_type", "physical").lower()
        period = request.query_params.get("period", "all").lower()
        summary = request.query_params.get("summary", "false").lower() == "true"

        try:
            year = int(request.query_params.get("year", date.today().year))
        except ValueError:
            return Response({"error": "Invalid year"}, status=status.HTTP_400_BAD_REQUEST)

        users = self._get_target_users(request)
        if not users:
            return Response({"error": "No matching users"}, status=status.HTTP_404_NOT_FOUND)

        if summary:
            today = date.today()
            ranges = self._get_ranges(year_type, year)
            titles = {"monthly": "monthly", "quarterly": "quarterly", "half": "half yearly", "annual": "annually"}
            summary_data = []
            
            for key in ["monthly", "quarterly", "half", "annual"]:
                # Find the current period that contains today's date
                current_range = None
                for start, end in ranges[key]:
                    if start <= today <= end:
                        current_range = (start, end)
                        break
                
                # If no current range found, use the first one as fallback
                if not current_range:
                    current_range = ranges[key][0] if ranges[key] else (today, today)
                
                start, end = current_range
                target = self._sum_targets(users, start, end)
                achieved = self._sum_achieved(users, start, end)
                pct = int(((achieved / target) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) if target else 0
                summary_data.append({
                    "title": titles[key],
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "target": float(target),
                    "achieved": float(achieved),
                    "percentage": pct,
                    "increase": pct > 50,
                })
            return Response(summary_data)

        # -------------------------
        # DETAILED MODE
        # -------------------------
        ranges = self._get_ranges(year_type, year)
        requested = [period] if period != "all" else ranges.keys()
        results = []

        for p in requested:
            data = []
            for start, end in ranges[p]:
                target = self._sum_targets(users, start, end)
                achieved = self._sum_achieved(users, start, end)
                pct = int(((achieved / target) * 100).quantize(Decimal("1"), ROUND_HALF_UP)) if target else 0
                data.append({
                    "label": f"{p.title()} {start.strftime('%b %Y')} - {end.strftime('%b %Y')}",
                    "start": start,
                    "end": end,
                    "target": float(target),
                    "achieved": float(achieved),
                    "percentage": pct,
                })
            results.append({"period_type": p, "items": data})
        return Response(results)