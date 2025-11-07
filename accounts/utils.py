from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

def create_targets_for_financial_and_physical_year_for_user(
    user,
    start_financial_year=None,
    end_financial_year=None,
    start_physical_year=None,
    end_physical_year=None,
    default_target=Decimal("0.00"),
    **kwargs
):
    """
    Create MonthlyTarget records for a single user for distinct
    financial years (Apr–Mar) and physical years (Jan–Dec).
    Avoids duplicate months between FY and PY.

    Args:
        user: User instance or user ID
        start_financial_year: Starting FY
        end_financial_year: Ending FY
        start_physical_year: Starting PY
        end_physical_year: Ending PY
        default_target: Default UserTarget value if missing

    Returns:
        Dictionary with creation statistics for that user
    """
    # Resolve user instance if ID is passed
    if isinstance(user, int):
        user = User.objects.get(id=user)

    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_fy = current_year if current_month >= 4 else current_year - 1

    start_fy = start_financial_year or current_fy
    end_fy = end_financial_year or current_fy
    start_py = start_physical_year or current_year
    end_py = end_physical_year or current_year

    stats = dict(
        user=user.username,
        user_target_created=False,
        monthly_targets_created=0,
        monthly_targets_existed=0,
        months_skipped_before_join=0,
        errors=[]
    )

    # --- Month-Year generation ---
    def generate_fy_months(fy):
        return [(m, fy) for m in range(4, 13)] + [(m, fy + 1) for m in range(1, 4)]

    def generate_py_months(py):
        return [(m, py) for m in range(1, 13)]

    fy_months = {m_y for fy in range(start_fy, end_fy + 1) for m_y in generate_fy_months(fy)}
    py_months = {m_y for py in range(start_py, end_py + 1) for m_y in generate_py_months(py)}
    all_months = sorted(fy_months.union(py_months), key=lambda x: (x[1], x[0]))

    print(f"👤 Processing user: {user.username}")
    print(f"📅 FY Range: {start_fy}-{end_fy+1}, PY Range: {start_py}-{end_py}")

    joined_date = user.date_joined.date()

    if today.year < joined_date.year or (today.year == joined_date.year and today.month < joined_date.month):
        print(f"⏳ Skipped: {user.username} joined on {joined_date} (after current date)")
        stats["errors"].append("User not yet joined")
        return stats

    # --- Create UserTarget ---
    from accounts.models import UserTarget, MonthlyTarget  # import here to avoid circulars
    user_target, created = UserTarget.objects.get_or_create(
        user=user, defaults={"target": default_target}
    )
    if created:
        stats["user_target_created"] = True
        print(f"🎯 Created UserTarget for {user.username}: {default_target}")

    # --- Create MonthlyTargets ---
    with transaction.atomic():
        for month, year in all_months:
            # Skip months before user joined
            if year < joined_date.year or (year == joined_date.year and month < joined_date.month):
                stats["months_skipped_before_join"] += 1
                continue

            _, mt_created = MonthlyTarget.objects.get_or_create(
                user=user,
                month=month,
                year=year,
                defaults={"target_amount": user_target.target},
            )
            if mt_created:
                stats["monthly_targets_created"] += 1
            else:
                stats["monthly_targets_existed"] += 1

    print(
        f"✅ Done: {user.username} | Created {stats['monthly_targets_created']} | "
        f"Existed {stats['monthly_targets_existed']} | Skipped {stats['months_skipped_before_join']}"
    )
    return stats
