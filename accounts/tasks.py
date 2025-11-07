"""
Django-Q tasks for monthly target calculations and adjustments
"""
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from .models import UserTarget, MonthlyTarget


def calculate_user_achieved_amount(user, month, year):
    """
    Calculate achieved amount for a user with weighted logic:
    - Full amount if user is both creator and assignee
    - Half amount if user is only creator or only assignee
    """
    from lead.models import Opportunity
    
    base_qs = Opportunity.objects.filter(
        opportunity_status=34,
        is_active=True,
        closing_date__month=month,
        closing_date__year=year
    )
    
    # Full amount: both creator and assignee
    both_value = Decimal(
        base_qs.filter(Q(lead__created_by=user) & Q(lead__assigned_to=user))
        .aggregate(total=Sum('opportunity_value'))['total'] or 0
    )
    
    # Half amount: only creator
    only_creator_value = Decimal(
        base_qs.filter(Q(lead__created_by=user) & ~Q(lead__assigned_to=user))
        .aggregate(total=Sum('opportunity_value'))['total'] or 0
    ) / 2
    
    # Half amount: only assignee
    only_assigned_value = Decimal(
        base_qs.filter(~Q(lead__created_by=user) & Q(lead__assigned_to=user))
        .aggregate(total=Sum('opportunity_value'))['total'] or 0
    ) / 2
    
    return both_value + only_creator_value + only_assigned_value


def adjust_monthly_targets(*args, **kwargs):
    """
    Adjust monthly targets based on actual opportunity achievements.
    
    Logic:
    - Get current month's target and achieved amount (from opportunities)
    - Compare achieved vs target for current month
    - If achieved > target: Reduce next month's target by the excess
    - If achieved < target: Increase next month's target by the shortfall
    
    This should be scheduled to run monthly via Django-Q
    """
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    # Calculate next month
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1
    
    # Get all users with targets (exclude admins)
    users_with_targets = UserTarget.objects.select_related('user').exclude(
        user__groups__name__iexact='Admin'
    )
    
    for user_target in users_with_targets:
        user = user_target.user
        user_overall_target = user_target.target
        print(f"\n=== Processing User: {user.username} (ID: {user.id}) ===")
        print(f"User Overall Target: {user_overall_target}")
        
        # Get current month's target
        try:
            current_monthly_target = MonthlyTarget.objects.get(
                user=user,
                month=current_month,
                year=current_year
            )
            current_target_amount = current_monthly_target.target_amount
            print(f"Current Monthly Target ({current_month}/{current_year}): {current_target_amount}")
        except MonthlyTarget.DoesNotExist:
            print(f"No current month target found for {user.username}, skipping...")
            continue
        
        # Calculate achieved amount with weighted logic
        achieved_amount = calculate_user_achieved_amount(user, current_month, current_year)
        print(f"Achieved Amount: {achieved_amount}")
        
        # Calculate difference between target and achieved
        difference = current_target_amount - achieved_amount
        print(f"Difference (Target - Achieved): {difference}")
        
        # Get or create next month's target
        next_monthly_target, created = MonthlyTarget.objects.get_or_create(
            user=user,
            month=next_month,
            year=next_year,
            defaults={'target_amount': user_overall_target}  # Default to overall target
        )
        print(f"Next Month Target ({next_month}/{next_year}) - Created: {created}, Current Value: {next_monthly_target.target_amount}")
        
        if difference > 0:
            # User achieved less than target (shortfall)
            # Increase next month's target to compensate
            increase = difference
            new_next_target = next_monthly_target.target_amount + increase
            next_monthly_target.target_amount = new_next_target
            next_monthly_target.save()
            print(f"⬆️ SHORTFALL: Increasing next month target by {increase} to {new_next_target}")
            
        elif difference < 0:
            # User achieved more than target (excess)
            # Reduce next month's target as reward/adjustment
            reduction = abs(difference)
            new_next_target = max(
                next_monthly_target.target_amount - reduction,
                Decimal('0.00')  # Don't go below 0
            )
            next_monthly_target.target_amount = new_next_target
            next_monthly_target.save()
            print(f"⬇️ EXCESS: Reducing next month target by {reduction} to {new_next_target}")
        else:
            print(f"✅ PERFECT: Target met exactly, no adjustment needed")
        
        # If difference == 0, no changes needed (perfectly met target)
    
    return f"Adjusted monthly targets for {users_with_targets.count()} users"


def create_monthly_targets_for_all_users(month=None, year=None, default_target=Decimal('0.00'), **kwargs):
    """
    Create MonthlyTarget for all users using their UserTarget value.
    If a UserTarget doesn't exist for a user, create one with the default_target value.
    
    Args:
        month: Target month (1-12), defaults to current month
        year: Target year, defaults to current year
        default_target: Default target amount if UserTarget doesn't exist
        **kwargs: Accept and ignore any extra kwargs passed by schedulers (e.g. 'months', 'repeats')
    
    Returns:
        Dictionary with creation statistics
    """
    # Extra kwargs from django-q schedule parameters are automatically ignored
    today = datetime.now()
    target_month = month or today.month
    target_year = year or today.year
    
    # Get all active users excluding admins
    all_users = User.objects.filter(is_active=True).exclude(
        groups__name__iexact='Admin'
    ).distinct()
    
    stats = {
        'total_users': 0,
        'monthly_targets_created': 0,
        'monthly_targets_existed': 0,
        'user_targets_created': 0,
        'errors': []
    }
    
    for user in all_users:
        try:
            stats['total_users'] += 1
            
            # Get or create UserTarget
            user_target, ut_created = UserTarget.objects.get_or_create(
                user=user,
                defaults={'target': default_target}
            )
            
            if ut_created:
                stats['user_targets_created'] += 1
                print(f"Created UserTarget for {user.username} with target {default_target}")
            
            # Get or create MonthlyTarget using UserTarget value
            monthly_target, mt_created = MonthlyTarget.objects.get_or_create(
                user=user,
                month=target_month,
                year=target_year,
                defaults={'target_amount': user_target.target}
            )
            
            if mt_created:
                stats['monthly_targets_created'] += 1
                print(f"Created MonthlyTarget for {user.username}: {user_target.target} for {target_month}/{target_year}")
            else:
                stats['monthly_targets_existed'] += 1
                print(f"MonthlyTarget already exists for {user.username} for {target_month}/{target_year}")
                
        except Exception as e:
            error_msg = f"Error processing user {user.username}: {str(e)}"
            stats['errors'].append(error_msg)
            print(error_msg)
    
    summary = (f"Processed {stats['total_users']} users: "
               f"{stats['monthly_targets_created']} monthly targets created, "
               f"{stats['monthly_targets_existed']} already existed, "
               f"{stats['user_targets_created']} user targets created, "
               f"{len(stats['errors'])} errors")
    
    print(f"\n=== Summary ===\n{summary}")
    return stats


from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_targets_for_financial_and_physical_year(
    start_financial_year=None,
    end_financial_year=None,
    start_physical_year=None,
    end_physical_year=None,
    default_target=Decimal("0.00"),
    **kwargs
):
    """
    Create MonthlyTarget records for all active users for distinct
    financial years (Apr–Mar) and physical years (Jan–Dec).
    Avoids duplicate months between FY and PY.
    
    Only creates targets for users where current date (month/year) >= user.date_joined (month/year).
    Also only creates monthly targets for months >= user's joining month/year.
    
    Args:
        start_financial_year: Starting financial year
        end_financial_year: Ending financial year  
        start_physical_year: Starting physical year
        end_physical_year: Ending physical year
        default_target: Default target amount for new UserTarget records
        
    Returns:
        Dictionary with creation statistics including skipped users
    """
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_fy = current_year if current_month >= 4 else current_year - 1

    # Default values
    start_fy = start_financial_year or current_fy
    end_fy = end_financial_year or current_fy
    start_py = start_physical_year or current_year
    end_py = end_physical_year or current_year

    users = User.objects.filter(is_active=True).exclude(groups__name__iexact="Admin").distinct()

    stats = dict(
        total_users=0,
        user_targets_created=0,
        monthly_targets_created=0,
        monthly_targets_existed=0,
        users_skipped_not_joined=0,
        errors=[]
    )

    # --- Month-Year generation helpers ---
    def generate_fy_months(fy):
        """Return list of (month, year) for a given FY e.g. 2024–25"""
        months = [(m, fy) for m in range(4, 13)]  # Apr–Dec of start year
        months += [(m, fy + 1) for m in range(1, 4)]  # Jan–Mar of next year
        return months

    def generate_py_months(py):
        """Return list of (month, year) for a given PY (Jan–Dec)"""
        return [(m, py) for m in range(1, 13)]

    # --- Build distinct (month, year) list ---
    fy_months = {m_y for fy in range(start_fy, end_fy + 1) for m_y in generate_fy_months(fy)}
    py_months = {m_y for py in range(start_py, end_py + 1) for m_y in generate_py_months(py)}

    all_months = sorted(fy_months.union(py_months), key=lambda x: (x[1], x[0]))

    print(f"Processing {len(all_months)} distinct months for FY {start_fy}-{end_fy+1} and PY {start_py}-{end_py}")

    # --- Process users ---
    for user in users:
        try:
            # Check if current date (month/year) >= user's joining date (month/year)
            joined_date = user.date_joined.date()  # Convert datetime to date
            
            if today.year < joined_date.year or (today.year == joined_date.year and today.month < joined_date.month):
                print(f"⏳ Skipping {user.username}: joined on {joined_date}, current date {today.strftime('%Y-%m-%d')} is before joining month/year")
                stats["users_skipped_not_joined"] += 1
                continue
                
            print(f"✅ Processing {user.username}: joined on {joined_date}, eligible for target creation")
            
            stats["total_users"] += 1
            user_target, created = UserTarget.objects.get_or_create(
                user=user, defaults={"target": default_target}
            )
            if created:
                stats["user_targets_created"] += 1

            with transaction.atomic():
                for month, year in all_months:
                    # Additional check: only create targets for months >= joining month/year
                    if year < joined_date.year or (year == joined_date.year and month < joined_date.month):
                        continue  # Skip months before user joined
                        
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
        except Exception as e:
            stats["errors"].append(f"{user.username}: {e}")

    print(
        f"Users: {stats['total_users']} processed | "
        f"Skipped (not joined yet): {stats['users_skipped_not_joined']} | "
        f"UserTargets Created: {stats['user_targets_created']} | "
        f"Monthly Created: {stats['monthly_targets_created']} | "
        f"Existed: {stats['monthly_targets_existed']} | "
        f"Errors: {len(stats['errors'])}"
    )
    return stats



def create_targets_from_start_to_current(
    start_financial_year=None,
    start_physical_year=None,
    default_target=Decimal("0.00"),
    **kwargs
):
    """
    Automatically create targets from start years to current FY/PY based on today's date.
    
    Logic:
    - Determines current financial year based on today's date (Apr-Mar cycle)
    - Determines current physical year based on today's date (Jan-Dec cycle)
    - If start years not provided, uses current years as both start and end
    - If start years provided, creates from start year to current year
    - Only processes users where current date >= user.date_joined (month/year comparison)
    - Only creates monthly targets for months >= user's joining month/year
    
    Args:
        start_financial_year: Starting financial year (defaults to current FY)
        start_physical_year: Starting physical year (defaults to current year)
        default_target: Default target amount for users without UserTarget
        **kwargs: Additional arguments passed to the main function
    
    Returns:
        Dictionary with creation statistics including skipped users
        
    Examples:
        # Current date: Nov 7, 2025 (FY 2025-26, PY 2025)
        create_targets_from_start_to_current()  # Creates for FY 2025 and PY 2025 only
        create_targets_from_start_to_current(start_financial_year=2020)  # Creates FY 2020-2025
    """
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    
    # Determine current financial year (Apr-Mar cycle)
    current_fy = current_year if current_month >= 4 else current_year - 1
    
    # Determine start years based on parameters or current year
    actual_start_fy = start_financial_year if start_financial_year is not None else current_fy
    actual_start_py = start_physical_year if start_physical_year is not None else current_year
    
    print(f"📅 Date Analysis: {today.strftime('%Y-%m-%d')}")
    print(f"📅 Current Financial Year: {current_fy} (FY {current_fy}-{current_fy+1})")
    print(f"📅 Current Physical Year: {current_year}")
    print(f"🎯 Creating targets from FY {actual_start_fy} to FY {current_fy}")
    print(f"🎯 Creating targets from PY {actual_start_py} to PY {current_year}")
    
    return create_targets_for_financial_and_physical_year(
        start_financial_year=actual_start_fy,
        end_financial_year=current_fy,
        start_physical_year=actual_start_py,
        end_physical_year=current_year,
        default_target=default_target,
        **kwargs,
    )
