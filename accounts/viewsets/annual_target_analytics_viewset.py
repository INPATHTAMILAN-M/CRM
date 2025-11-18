from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from accounts.models import MonthlyTarget, Teams
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

            return User.objects.filter(is_active=True).exclude(groups__name__iexact="admin")

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

    def _sum_targets(self, users, start, end):
        months = []
        cur = start.replace(day=1)
        while cur <= end:
            months.append((cur.month, cur.year))
            cur = (cur + relativedelta(months=1)).replace(day=1)

        q = Q()
        for m, y in months:
            q |= Q(month=m, year=y)
        total = MonthlyTarget.objects.filter(q, user__in=users).aggregate(
            total=Sum("target_amount")
        )["total"]
        return Decimal(total or 0)

    def _sum_achieved(self, users, start, end):
        qs = Opportunity.objects.filter(
            opportunity_status=34,
            is_active=True,
            closing_date__range=(start, end),
        )
        total = Decimal("0.00")

        for u in users:
            # Define filters with weights - same logic as target_analytics_viewset
            filters_with_weights = [
                (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),   # both roles → full
                (Q(lead__created_by=u) & ~Q(lead__assigned_to=u), 0.5), # only creator → half
                (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5), # only assigned → half
            ]

            for condition, weight in filters_with_weights:
                value = qs.filter(condition).aggregate(total=Sum("opportunity_value"))["total"] or 0
                total += Decimal(value) * Decimal(weight)

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
