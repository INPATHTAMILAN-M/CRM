#!/usr/bin/env python
"""Debug: check weighted achieved for previous month specifically."""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
sys.path.insert(0, '/home/CRM')
django.setup()

from datetime import date
from decimal import Decimal
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from lead.models import Opportunity
from accounts.models import MonthlyTarget, UserActiveHistory
from django.utils import timezone
from dateutil.relativedelta import relativedelta

today = date.today()
prev_date = today - relativedelta(months=1)
current_month = today.month
current_year = today.year
prev_month = prev_date.month
prev_year = prev_date.year

# Replicate month_year_allowed from the viewset
def month_year_gte(month, year, start_month, start_year):
    return year > start_year or (year == start_year and month >= start_month)

def month_year_lte(month, year, end_month, end_year):
    return year < end_year or (year == end_year and month <= end_month)

def month_year_in_range(month, year, start, end=None, inclusive_end=True):
    if not month_year_gte(month, year, start.month, start.year):
        return False
    if end is None:
        return True
    if inclusive_end:
        return month_year_lte(month, year, end.month, end.year)
    return year < end.year or (year == end.year and month < end.month)

def month_year_allowed(target_user, month, year):
    histories = list(UserActiveHistory.objects.filter(user=target_user).order_by('changed_at'))
    month_histories = [h for h in histories if h.changed_at.year == year and h.changed_at.month == month]
    if month_histories:
        return bool(month_histories[-1].is_active)
    if not histories:
        return bool(target_user.is_active)
    active_start = None
    if histories and not histories[0].is_active and target_user.date_joined:
        active_start = target_user.date_joined
        if month_year_in_range(month, year, active_start, histories[0].changed_at, inclusive_end=False):
            return True
        active_start = None
    for h in histories:
        if h.is_active:
            if active_start is None:
                active_start = h.changed_at
                if h == histories[0] and target_user.date_joined and target_user.date_joined < active_start:
                    active_start = target_user.date_joined
        else:
            if active_start is not None:
                if month_year_in_range(month, year, active_start, h.changed_at, inclusive_end=False):
                    return True
                active_start = None
    if active_start is not None:
        if target_user.is_active:
            return month_year_in_range(month, year, active_start)
        return month_year_in_range(month, year, active_start, timezone.now(), inclusive_end=False)
    if target_user.is_active:
        return month_year_in_range(month, year, timezone.now())
    return False

print("="*80)
print(f"Checking month_year_allowed for PREVIOUS MONTH ({prev_month}/{prev_year})")
print("="*80)

all_users = User.objects.all()
for u in all_users:
    allowed = month_year_allowed(u, prev_month, prev_year)
    print(f"  User {u.username} (id={u.id}, active={u.is_active}): allowed={allowed}")

print(f"\n{'='*80}")
print(f"Weighted achieved for PREV MONTH ({prev_month}/{prev_year})")
print("="*80)

total_weighted = Decimal('0.00')
for u in all_users:
    if not month_year_allowed(u, prev_month, prev_year):
        continue
    qs = Opportunity.objects.filter(opportunity_status=34, is_active=True,
                                     closing_date__month=prev_month,
                                     closing_date__year=prev_year)
    user_total = Decimal('0.00')
    filters_with_weights = [
        (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1, "both"),
        (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1, "created_only_null"),
        (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5, "created_diff_assigned"),
        (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5, "assigned_only"),
    ]
    for condition, weight, label in filters_with_weights:
        value = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
        if value:
            user_total += Decimal(value) * Decimal(weight)
            print(f"  User {u.username}: {label} => value={value}, weight={weight}")
    if user_total > 0:
        print(f"  User {u.username}: TOTAL = {user_total}")
    total_weighted += user_total

print(f"\nTotal weighted (prev month): {total_weighted}")
print(f"API returned: 133000.00")

# Without month_year_allowed check
print(f"\n{'='*80}")
print(f"Without month_year_allowed filter:")
print("="*80)
total_no_filter = Decimal('0.00')
for u in all_users:
    qs = Opportunity.objects.filter(opportunity_status=34, is_active=True,
                                     closing_date__month=prev_month,
                                     closing_date__year=prev_year)
    user_total = Decimal('0.00')
    for condition, weight, label in [
        (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1, "both"),
        (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1, "created_only_null"),
        (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5, "created_diff_assigned"),
        (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5, "assigned_only"),
    ]:
        value = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
        if value:
            user_total += Decimal(value) * Decimal(weight)
            print(f"  User {u.username}: {label} => value={value}, weight={weight}")
    if user_total > 0:
        print(f"  User {u.username}: TOTAL = {user_total}")
    total_no_filter += user_total

print(f"\nTotal without filter: {total_no_filter}")

# Also check: FINANCIAL YEAR
print(f"\n{'='*80}")
print(f"Financial Year achieved breakdown")
print("="*80)
fy_start_year = current_year if today.month >= 4 else current_year - 1
fy_start = date(fy_start_year, 4, 1)
fy_end = date(fy_start_year + 1, 3, 31)

def month_year_pairs(start_date, end_date):
    pairs = []
    cur = start_date.replace(day=1)
    while cur <= end_date:
        pairs.append((cur.month, cur.year))
        cur = (cur + relativedelta(months=1)).replace(day=1)
    return pairs

fy_total = Decimal('0.00')
for m, y in month_year_pairs(fy_start, fy_end):
    month_total = Decimal('0.00')
    for u in all_users:
        qs = Opportunity.objects.filter(opportunity_status=34, is_active=True,
                                         closing_date__month=m, closing_date__year=y)
        for condition, weight in [
            (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
            (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
            (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
            (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
        ]:
            value = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
            month_total += Decimal(value) * Decimal(weight)
    if month_total > 0:
        print(f"  Month {m}/{y}: {month_total}")
    fy_total += month_total

print(f"FY total (no active filter): {fy_total}")
print(f"API returned: 367299.00")

# Raw FY total
raw_fy = Opportunity.objects.filter(
    opportunity_status=34, is_active=True,
    closing_date__gte=fy_start, closing_date__lte=fy_end
).aggregate(total=Sum('opportunity_value'))['total'] or 0
print(f"Raw FY total: {raw_fy}")

# Physical Year
print(f"\n{'='*80}")
print(f"Physical Year achieved breakdown")
print("="*80)
py_start = date(current_year, 1, 1)
py_end = date(current_year, 12, 31)

py_total = Decimal('0.00')
for m, y in month_year_pairs(py_start, py_end):
    month_total = Decimal('0.00')
    for u in all_users:
        qs = Opportunity.objects.filter(opportunity_status=34, is_active=True,
                                         closing_date__month=m, closing_date__year=y)
        for condition, weight in [
            (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
            (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
            (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
            (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
        ]:
            value = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
            month_total += Decimal(value) * Decimal(weight)
    if month_total > 0:
        print(f"  Month {m}/{y}: {month_total}")
    py_total += month_total

print(f"PY total (no active filter): {py_total}")
print(f"API returned: 680478.00")

raw_py = Opportunity.objects.filter(
    opportunity_status=34, is_active=True,
    closing_date__gte=py_start, closing_date__lte=py_end
).aggregate(total=Sum('opportunity_value'))['total'] or 0
print(f"Raw PY total: {raw_py}")
