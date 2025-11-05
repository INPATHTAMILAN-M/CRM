from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from accounts.models import MonthlyTarget, Teams
from lead.models import Opportunity, Lead


class AnnualTargetAnalyticsViewSet(viewsets.ViewSet):
    """Provides annual analytics for financial or physical year."""

    permission_classes = [IsAuthenticated]

    # ---------------- Helper Methods ---------------- #

    def _get_year_range(self, year_type, year):
        return (date(year, 4, 1), date(year + 1, 3, 31)) if year_type == 'financial' else (date(year, 1, 1), date(year, 12, 31))

    def _month_year_pairs(self, start, end):
        pairs, cur = [], start.replace(day=1)
        while cur <= end:
            pairs.append((cur.month, cur.year))
            cur = (cur + relativedelta(months=1)).replace(day=1)
        return pairs

    def _sum_targets(self, users, start, end):
        q = Q()
        for m, y in self._month_year_pairs(start, end):
            q |= Q(month=m, year=y)
        total = MonthlyTarget.objects.filter(q, user__in=users).aggregate(total=Sum('target_amount'))['total'] or 0
        return Decimal(total)

    def _sum_achieved(self, users, start, end):
        total = Decimal('0.00')
        opps = Opportunity.objects.filter(opportunity_status=34, is_active=True, closing_date__range=(start, end))
        for u in users:
            both = opps.filter(Q(lead__created_by=u) & Q(lead__assigned_to=u)).aggregate(Sum('opportunity_value'))['opportunity_value__sum'] or 0
            created = opps.filter(Q(lead__created_by=u) & ~Q(lead__assigned_to=u)).aggregate(Sum('opportunity_value'))['opportunity_value__sum'] or 0
            assigned = opps.filter(~Q(lead__created_by=u) & Q(lead__assigned_to=u)).aggregate(Sum('opportunity_value'))['opportunity_value__sum'] or 0
            total += Decimal(both) + Decimal(created)/2 + Decimal(assigned)/2
        return total

    def _resolve_users(self, request):
        User = get_user_model()
        user = request.user
        if not user.groups.filter(name__iexact='admin').exists():
            return [user]

        params = request.query_params
        if user_id := params.get('user_id'):
            return User.objects.filter(id=user_id)
        if team_id := params.get('team_id'):
            team = Teams.objects.filter(id=team_id).first()
            return [team.bdm_user, *team.bde_user.all()] if team else []
        if company := params.get('company_name'):
            leads = Lead.objects.filter(name__icontains=company)
            ids = {l.created_by_id for l in leads if l.created_by_id} | {l.assigned_to_id for l in leads if l.assigned_to_id}
            return User.objects.filter(id__in=ids)
        return User.objects.filter(is_active=True).exclude(groups__name__iexact='admin')

    def _period_range(self, today, mode):
        """Return (current, previous) period ranges based on mode."""
        if mode == 'monthly':
            start = today.replace(day=1)
            prev = (start - relativedelta(months=1)).replace(day=1)
            end = (start + relativedelta(months=1)) - relativedelta(days=1)
            prev_end = (prev + relativedelta(months=1)) - relativedelta(days=1)
        elif mode == 'quarterly':
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start = date(today.year, start_month, 1)
            end = start + relativedelta(months=3, days=-1)
            prev = start - relativedelta(months=3)
            prev_end = prev + relativedelta(months=3, days=-1)
        elif mode == 'half':
            half = 1 if today.month <= 6 else 2
            start = date(today.year, 1 if half == 1 else 7, 1)
            end = start + relativedelta(months=6, days=-1)
            prev = start - relativedelta(months=6)
            prev_end = prev + relativedelta(months=6, days=-1)
        else:  # annual
            start, end = date(today.year, 1, 1), date(today.year, 12, 31)
            prev, prev_end = date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)
        return (start, end), (prev, prev_end)

    # ---------------- Main Endpoint ---------------- #

    @extend_schema(
        parameters=[
            OpenApiParameter('year_type', OpenApiTypes.STR, description="'financial' or 'physical'"),
            OpenApiParameter('period', OpenApiTypes.STR, description="'monthly'|'quarterly'|'half'|'annual'|'all'"),
            OpenApiParameter('year', OpenApiTypes.INT, description="Start year for financial or calendar year."),
            OpenApiParameter('summary', OpenApiTypes.BOOL, description="If true, returns summarized view."),
            OpenApiParameter('user_id', OpenApiTypes.INT),
            OpenApiParameter('team_id', OpenApiTypes.INT),
            OpenApiParameter('company_name', OpenApiTypes.STR),
        ]
    )
    @action(detail=False, methods=['get'], url_path='annual-analytics')
    def get_annual_analytics(self, request):
        year_type = request.query_params.get('year_type', 'physical')
        period = request.query_params.get('period', 'all')
        summary = request.query_params.get('summary', 'false').lower() == 'true'
        year = int(request.query_params.get('year', date.today().year))
        users = self._resolve_users(request)
        if not users:
            return Response({'error': 'No matching users found.'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        result = []
        modes = [period] if period != 'all' else ['monthly', 'quarterly', 'half', 'annual']

        for mode in modes:
            if summary:
                (cur_s, cur_e), (prev_s, prev_e) = self._period_range(today, mode)
                cur_target = self._sum_targets(users, cur_s, cur_e)
                cur_ach = self._sum_achieved(users, cur_s, cur_e)
                prev_ach = self._sum_achieved(users, prev_s, prev_e)

                pct = int(((cur_ach / cur_target) * 100).quantize(Decimal('1'), ROUND_HALF_UP)) if cur_target else 0
                result.append({
                    'title': mode.title(),
                    'target': cur_target,
                    'achieved': cur_ach,
                    'increase': cur_ach > prev_ach,
                    'percentage': pct
                })
            else:
                start, end = self._get_year_range(year_type, year)
                details = []
                step = {'monthly': 1, 'quarterly': 3, 'half': 6, 'annual': 12}[mode]
                cur = start
                while cur <= end:
                    label = f"{cur.strftime('%b %Y')}" if mode == 'monthly' else f"{mode.title()} {cur.year}"
                    next_date = cur + relativedelta(months=step)
                    s_end = min(next_date - relativedelta(days=1), end)
                    t = self._sum_targets(users, cur, s_end)
                    a = self._sum_achieved(users, cur, s_end)
                    pct = int(((a / t) * 100).quantize(Decimal('1'), ROUND_HALF_UP)) if t else 0
                    details.append({'label': label, 'target': t, 'achieved': a, 'percentage': pct})
                    cur = next_date
                result.append({'period_type': mode, 'items': details})

        return Response(result, status=status.HTTP_200_OK)
