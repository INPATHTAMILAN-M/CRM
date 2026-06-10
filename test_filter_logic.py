#!/usr/bin/env python3
"""Test the month overlap logic for active history filtering."""

from datetime import datetime

# Simulated user 18 history events
history_events = [
    {'is_active': True, 'changed_at': datetime(2025, 1, 6)},
    {'is_active': False, 'changed_at': datetime(2026, 6, 6, 5, 4, 57)},
    {'is_active': True, 'changed_at': datetime(2026, 6, 6, 5, 6, 7)},
    {'is_active': False, 'changed_at': datetime(2026, 6, 6, 5, 6, 16)},
    {'is_active': True, 'changed_at': datetime(2026, 6, 6, 5, 6, 52)},
    {'is_active': False, 'changed_at': datetime(2026, 6, 6, 5, 16, 58)},
    {'is_active': True, 'changed_at': datetime(2026, 6, 6, 5, 17, 15)},
    {'is_active': False, 'changed_at': datetime(2026, 6, 6, 5, 19, 31)},
    {'is_active': True, 'changed_at': datetime(2026, 6, 6, 5, 54, 5)},
    {'is_active': False, 'changed_at': datetime(2026, 6, 6, 9, 1, 44)},
    {'is_active': True, 'changed_at': datetime(2026, 6, 6, 9, 2, 26)},
]

# Build periods (simulating the viewset logic)
periods = []
active_start = None

for h in history_events:
    if h['is_active']:
        if active_start is None:
            active_start = h['changed_at']
    else:
        if active_start is not None:
            periods.append((active_start, h['changed_at']))
            active_start = None

# Assume user is currently inactive (is_active = False)
user_is_active = False

if active_start is not None:
    if user_is_active:
        periods.append((active_start, None))
    else:
        # User is inactive, so the active period ended at now
        now = datetime(2026, 6, 6, 10, 0, 0)  # Assuming current time
        periods.append((active_start, now))
elif user_is_active:
    # Current user is active but no open active period in history
    periods.append((datetime(2026, 6, 6, 10, 0, 0), None))

print("Active periods for user 18:")
for start, end in periods:
    end_str = end.strftime('%Y-%m-%d %H:%M:%S') if end else "None (ongoing)"
    print(f"  {start.strftime('%Y-%m-%d %H:%M:%S')} to {end_str}")

print("\nChecking which months each period covers:")

def check_month_in_period(year, month, start, end):
    """Check if a month is included in a period (excluding months with inactivation)."""
    sy, sm = start.year, start.month
    
    # Period starts before month end: year > sy OR (year = sy AND month >= sm)
    cond_starts_before = year > sy or (year == sy and month >= sm)
    
    if end:
        ey, em = end.year, end.month
        # For ended periods, exclude the month where inactivation occurred
        # Only include months BEFORE the end month
        cond_ends_before_month = year < ey or (year == ey and month < em)
        return cond_starts_before and cond_ends_before_month
    else:
        # No end date - ongoing active period
        return cond_starts_before

# Test for April, May, June 2026
for month_num in [4, 5, 6]:
    print(f"\n2026-{month_num:02d}:")
    included = False
    for i, (start, end) in enumerate(periods):
        if check_month_in_period(2026, month_num, start, end):
            end_str = end.strftime('%Y-%m-%d') if end else "ongoing"
            print(f"  ✓ Included by period {i}: {start.strftime('%Y-%m-%d')} to {end_str}")
            included = True
    if not included:
        print(f"  ✗ NOT included by any period")
