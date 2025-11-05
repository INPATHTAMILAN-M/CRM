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
    """
    Provides annual analytics for two year types (financial Apr-Mar and physical Jan-Dec).

    Query params:
      - year_type: 'financial' or 'physical' (default: 'physical')
      - period: 'monthly'|'quarterly'|'half'|'annual'|'all' (default: 'all')
      - year: integer year (for financial, use start year, e.g. 2024 means Apr-2024..Mar-2025)
      - user_id, team_id, company_name (filter scope)
      - aggregate: 'true' or 'false'
    """
    permission_classes = [IsAuthenticated]

    # ---------------- Helper Methods ---------------- #

    def _get_year_range(self, year_type, year):
        """Return start and end date based on year type."""
        if year_type == 'financial':
            return date(year, 4, 1), date(year + 1, 3, 31)
        return date(year, 1, 1), date(year, 12, 31)

    def _get_period_ranges(self, year_type, year):
        """Return date ranges for monthly, quarterly, half-yearly, and annual periods."""
        start_date, end_date = self._get_year_range(year_type, year)
        ranges = {'monthly': [], 'quarterly': [], 'half': [], 'annual': []}

        # Monthly
        cur = start_date
        while cur <= end_date:
            start = cur.replace(day=1)
            next_month = start + relativedelta(months=1)
            end = next_month - relativedelta(days=1)
            ranges['monthly'].append((start.strftime('%b %Y'), start, end))
            cur = next_month

        # Quarterly (every 3 months)
        q_start = start_date
        q_index = 1
        while q_start <= end_date:
            q_end = (q_start + relativedelta(months=3)) - relativedelta(days=1)
            label = f"Q{q_index} {q_start.year}"
            ranges['quarterly'].append((label, q_start, min(q_end, end_date)))
            q_start = q_end + relativedelta(days=1)
            q_index += 1

        # Half-yearly
        h1_end = (start_date + relativedelta(months=6)) - relativedelta(days=1)
        h2_start = h1_end + relativedelta(days=1)
        ranges['half'] = [
            (f'H1 {year}', start_date, min(h1_end, end_date)),
            (f'H2 {year}', h2_start, end_date)
        ]

        # Annual
        ranges['annual'] = [(f'{year_type.title()} Year {year}', start_date, end_date)]

        return ranges

    def _month_year_pairs(self, start, end):
        """Generate (month, year) pairs for given date range."""
        pairs, cur = [], start.replace(day=1)
        while cur <= end:
            pairs.append((cur.month, cur.year))
            cur = (cur + relativedelta(months=1)).replace(day=1)
        return pairs

    def _get_total_target(self, users, start, end):
        """Sum of MonthlyTarget target_amount for users in given date range."""
        pairs = self._month_year_pairs(start, end)
        if not pairs:
            return Decimal('0.00')
        q = Q()
        for m, y in pairs:
            q |= Q(month=m, year=y)
        return Decimal(MonthlyTarget.objects.filter(q, user__in=users).aggregate(total=Sum('target_amount'))['total'] or 0)

    def _get_total_achieved(self, users, start, end):
        """Calculate achieved value with weighting logic."""
        total = Decimal('0.00')
        opportunities = Opportunity.objects.filter(
            opportunity_status=34, is_active=True,
            closing_date__range=(start, end)
        )

        for u in users:
            both = Decimal(opportunities.filter(Q(lead__created_by=u) & Q(lead__assigned_to=u))
                           .aggregate(total=Sum('opportunity_value'))['total'] or 0)
            created_only = Decimal(opportunities.filter(Q(lead__created_by=u) & ~Q(lead__assigned_to=u))
                                   .aggregate(total=Sum('opportunity_value'))['total'] or 0) / 2
            assigned_only = Decimal(opportunities.filter(~Q(lead__created_by=u) & Q(lead__assigned_to=u))
                                    .aggregate(total=Sum('opportunity_value'))['total'] or 0) / 2
            total += both + created_only + assigned_only

        return total

    def _get_target_users(self, request):
        """Resolve target users based on user/team/company filters."""
        User = get_user_model()
        user = request.user
        if not user.groups.filter(name__iexact='admin').exists():
            return [user]

        user_id = request.query_params.get('user_id')
        team_id = request.query_params.get('team_id')
        company_name = request.query_params.get('company_name')

        if user_id:
            return User.objects.filter(id=user_id)
        if team_id:
            team = Teams.objects.filter(id=team_id).first()
            return [team.bdm_user, *team.bde_user.all()] if team else []
        if company_name:
            leads = Lead.objects.filter(name__icontains=company_name)
            ids = {l.created_by_id for l in leads if l.created_by_id} | {l.assigned_to_id for l in leads if l.assigned_to_id}
            return User.objects.filter(id__in=ids)
        return User.objects.filter(is_active=True).exclude(groups__name__iexact='admin')

    # ---------------- Main Endpoint ---------------- #

    @extend_schema(
        parameters=[
            OpenApiParameter('year_type', OpenApiTypes.STR, description="'financial' or 'physical'"),
            OpenApiParameter('period', OpenApiTypes.STR, description="'monthly'|'quarterly'|'half'|'annual'|'all'"),
            OpenApiParameter('year', OpenApiTypes.INT, description="Year (start year for financial)"),
            OpenApiParameter('summary', OpenApiTypes.STR, description="'true' or 'false'"),
            OpenApiParameter('user_id', OpenApiTypes.INT, description="User filter"),
            OpenApiParameter('team_id', OpenApiTypes.INT, description="Team filter"),
            OpenApiParameter('company_name', OpenApiTypes.STR, description="Company filter"),
        ]
    )
    @action(detail=False, methods=['get'], url_path='annual-analytics')
    def get_annual_analytics(self, request):
        year_type = request.query_params.get('year_type', 'physical')
        period = request.query_params.get('period', 'all')
        summary = request.query_params.get('summary', 'false').lower() == 'true'
        year = int(request.query_params.get('year', date.today().year))

        users = self._get_target_users(request)
        if not users:
            return Response({'error': 'No matching users found.'}, status=status.HTTP_404_NOT_FOUND)

        ranges = self._get_period_ranges(year_type, year)
        requested_periods = [period] if period != 'all' else ['monthly', 'quarterly', 'half', 'annual']

        result = []

        for p in requested_periods:
            if summary:
                total_target = total_achieved = Decimal('0.00')
                for _, start, end in ranges[p]:
                    total_target += self._get_total_target(users, start, end)
                    total_achieved += self._get_total_achieved(users, start, end)

                percentage = int(((total_achieved / total_target) * 100).quantize(Decimal('1'), ROUND_HALF_UP)) if total_target else 0

                prev_year = year - 1
                prev_total = sum(self._get_total_achieved(users, s, e) for _, s, e in self._get_period_ranges(year_type, prev_year)[p])
                increase = total_achieved > prev_total

                title_map = {'monthly': 'Monthly', 'quarterly': 'Quarterly', 'half': 'Half Yearly', 'annual': 'Annually'}
                result.append({
                    'title': title_map.get(p, p),
                    'target': total_target,
                    'achieved': total_achieved,
                    'increase': increase,
                    'percentage': percentage
                })

            else:
                details = []
                for label, start, end in ranges[p]:
                    target = self._get_total_target(users, start, end)
                    achieved = self._get_total_achieved(users, start, end)
                    pct = int(((achieved / target) * 100).quantize(Decimal('1'), ROUND_HALF_UP)) if target else 0
                    details.append({
                        'label': label,
                        'start': start,
                        'end': end,
                        'target': target,
                        'achieved': achieved,
                        'percentage': pct
                    })
                result.append({'period_type': p, 'items': details})

        return Response(result)
