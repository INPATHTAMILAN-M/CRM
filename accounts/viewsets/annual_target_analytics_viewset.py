from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from accounts.models import MonthlyTarget, Teams
from accounts.serializers.target_analytics_serializer import TargetAnalyticsSerializer
from lead.models import Opportunity, Lead


class AnnualTargetAnalyticsViewSet(viewsets.ViewSet):
    """Provides annual analytics for two year types (financial Apr-Mar and physical Jan-Dec)

    Query params:
      - year_type: 'financial' or 'physical' (default: 'physical')
      - period: 'monthly'|'quarterly'|'half'|'annual'|'all' (default: 'all')
      - year: integer year (for financial, use start year, e.g. 2024 means Apr-2024..Mar-2025)
      - user_id, team_id, company_name (same selection rules as existing analytics)
    """
    permission_classes = [IsAuthenticated]

    def _period_ranges(self, year_type, year):
        """Return dicts of period label -> (start_date, end_date) depending on period granularity.
        year_type: 'financial' or 'physical'
        year: int
        """
        ranges = {}
        if year_type == 'financial':
            # Financial year starts April of 'year' and ends March of 'year+1'
            fy_start = date(year, 4, 1)
            fy_end = date(year + 1, 3, 31)
        else:
            # Physical calendar year Jan-Dec
            fy_start = date(year, 1, 1)
            fy_end = date(year, 12, 31)

        # Monthly ranges
        cur = fy_start
        while cur <= fy_end:
            start = cur.replace(day=1)
            next_month = (start + relativedelta(months=1))
            end = (next_month - relativedelta(days=1))
            label = start.strftime('%b %Y')
            ranges.setdefault('monthly', []).append((label, start, end))
            cur = next_month

        # Quarterly ranges (3-months)
        q_start = fy_start
        quarter_idx = 1
        while q_start <= fy_end:
            q_end = (q_start + relativedelta(months=3)) - relativedelta(days=1)
            label = f'Q{quarter_idx} {q_start.year if year_type=="physical" else (q_start.year if q_start.month>=4 else q_start.year-1)}'
            ranges.setdefault('quarterly', []).append((label, q_start, min(q_end, fy_end)))
            q_start = q_end + relativedelta(days=1)
            quarter_idx += 1

        # Half yearly (6 months)
        h1_start = fy_start
        h1_end = (h1_start + relativedelta(months=6)) - relativedelta(days=1)
        h2_start = h1_end + relativedelta(days=1)
        h2_end = fy_end
        ranges['half'] = [(
            'H1 ' + str(year), h1_start, min(h1_end, fy_end)
        ), (
            'H2 ' + str(year), h2_start, h2_end
        )]

        # Annual
        ranges['annual'] = [(f'{year_type.title()} Year {year}', fy_start, fy_end)]

        return ranges

    def _month_year_pairs(self, start_date, end_date):
        pairs = []
        cur = start_date.replace(day=1)
        while cur <= end_date:
            pairs.append((cur.month, cur.year))
            cur = (cur + relativedelta(months=1)).replace(day=1)
        return pairs

    def _sum_monthly_targets(self, users, start_date, end_date):
        pairs = self._month_year_pairs(start_date, end_date)
        if not pairs:
            return Decimal('0.00')
        q = Q()
        for m, y in pairs:
            q |= Q(month=m, year=y)
        qs = MonthlyTarget.objects.filter(q, user__in=users)
        return Decimal(qs.aggregate(total=Sum('target_amount')).get('total') or 0)

    def _calc_achieved_for_period(self, users, start_date, end_date):
        """Calculate achieved amount for a set of users within date range using weighted logic."""
        total = Decimal('0.00')
        base_qs = Opportunity.objects.filter(
            opportunity_status=34,
            is_active=True,
            closing_date__gte=start_date,
            closing_date__lte=end_date,
        )
        for u in users:
            both = Decimal(base_qs.filter(Q(lead__created_by=u) & Q(lead__assigned_to=u)).aggregate(total=Sum('opportunity_value'))['total'] or 0)
            only_creator = Decimal(base_qs.filter(Q(lead__created_by=u) & ~Q(lead__assigned_to=u)).aggregate(total=Sum('opportunity_value'))['total'] or 0) / 2
            only_assigned = Decimal(base_qs.filter(~Q(lead__created_by=u) & Q(lead__assigned_to=u)).aggregate(total=Sum('opportunity_value'))['total'] or 0) / 2
            total += both + only_creator + only_assigned
        return total

    @extend_schema(
        parameters=[
            OpenApiParameter(name='year_type', description="'financial' or 'physical'", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='period', description="'monthly'|'quarterly'|'half'|'annual'|'all'", required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='year', description='Year (integer). For financial, use start year e.g. 2024 for Apr-2024..Mar-2025', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='user_id', description='Filter by user id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='team_id', description='Filter by team id', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='company_name', description='Filter by company name (lead name)', required=False, type=OpenApiTypes.STR),
        ]
    )
    @action(detail=False, methods=['get'], url_path='annual-analytics')
    def annual_analytics(self, request):
        User = get_user_model()
        user = request.user
        is_admin = user.groups.filter(name__iexact='admin').exists()

        # Inputs
        year_type = request.query_params.get('year_type', 'physical')
        period = request.query_params.get('period', 'all')
        year = request.query_params.get('year')

        try:
            year = int(year) if year else date.today().year
        except ValueError:
            return Response({'error': 'Invalid year'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine target users same as existing view
        if is_admin:
            user_id = request.query_params.get('user_id')
            company_name = request.query_params.get('company_name')
            team_id = request.query_params.get('team_id')

            if user_id:
                target_users = User.objects.filter(id=user_id)
            elif team_id:
                team = Teams.objects.filter(id=team_id).first()
                if not team:
                    return Response({'error': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
                target_users = [team.bdm_user, *team.bde_user.all()]
            elif company_name:
                leads = Lead.objects.filter(name__icontains=company_name)
                user_ids = {l.created_by_id for l in leads if l.created_by_id} | {l.assigned_to_id for l in leads if l.assigned_to_id}
                target_users = User.objects.filter(id__in=user_ids)
            else:
                target_users = User.objects.filter(is_active=True).exclude(groups__name__iexact='admin')
        else:
            target_users = [user]

        if not target_users:
            return Response({'error': 'No matching users found.'}, status=status.HTTP_404_NOT_FOUND)

        ranges = self._period_ranges(year_type, year)

        periods_to_return = []
        requested = [period] if period != 'all' else ['monthly', 'quarterly', 'half', 'annual']

        for p in requested:
            period_list = []
            for label, start, end in ranges.get(p, []):
                target_sum = self._sum_monthly_targets(target_users, start, end)
                achieved = self._calc_achieved_for_period(target_users, start, end)
                pct = 0
                if target_sum:
                    pct = int(((Decimal(str(achieved)) / Decimal(str(target_sum))) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
                period_list.append({
                    'label': label,
                    'start': start,
                    'end': end,
                    'target': target_sum,
                    'achieved': achieved,
                    'percentage': pct,
                })
            periods_to_return.append({'period_type': p, 'items': period_list})

        return Response(periods_to_return)
