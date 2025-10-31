"""
Django-Q tasks for monthly target calculations and adjustments
"""
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.models import User
from .models import UserTarget, MonthlyTarget


def adjust_monthly_targets():
    """
    Adjust monthly targets based on actual opportunity achievements.
    
    Logic:
    - Get current month's target and achieved amount (from opportunities)
    - Compare achieved vs target for current month
    - If achieved > target: Reduce next month's target by the excess
    - If achieved < target: Increase next month's target by the shortfall
    
    This should be scheduled to run monthly via Django-Q
    """
    from django.db.models import Sum, Q
    from lead.models import Opportunity
    
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    # Calculate next month
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1
    
    # Get all users with targets (exclude admins)
    users_with_targets = UserTarget.objects.select_related('user').exclude(
        user__groups__name__iexact='admin'
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
        
        # Get achieved amount from opportunities (same logic as analytics viewset)
        opportunities = Opportunity.objects.filter(
            Q(lead__created_by=user) | Q(lead__assigned_to=user),
            closing_date__month=current_month,
            closing_date__year=current_year,
            opportunity_status=34,  # Closed/Won status
            is_active=True
        )
        
        opportunity_count = opportunities.count()
        achieved_result = opportunities.aggregate(total=Sum('opportunity_value'))
        achieved_amount = Decimal(achieved_result.get('total') or 0)
        print(f"Opportunities Found: {opportunity_count}")
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


def calculate_user_monthly_target(user_id, month=None, year=None):
    """
    Calculate and set monthly target for a specific user.
    
    Args:
        user_id: User ID
        month: Month (1-12), defaults to current month
        year: Year, defaults to current year
    
    Returns:
        MonthlyTarget instance or None
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    
    # Don't create targets for admin users
    if user.groups.filter(name__iexact='admin').exists():
        return None
    
    # Get user's overall target
    try:
        user_target = UserTarget.objects.get(user=user)
    except UserTarget.DoesNotExist:
        return None
    
    # Use current month/year if not provided
    if month is None or year is None:
        today = datetime.now()
        month = month or today.month
        year = year or today.year
    
    # Create or update monthly target
    monthly_target, created = MonthlyTarget.objects.update_or_create(
        user=user,
        month=month,
        year=year,
        defaults={'target_amount': user_target.target}
    )
    
    return monthly_target


def recalculate_all_monthly_targets():
    """
    Recalculate monthly targets for all users for the current month.
    Useful for initial setup or monthly reset.
    """
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    user_targets = UserTarget.objects.select_related('user').exclude(
        user__groups__name__iexact='admin'
    )
    
    count = 0
    for user_target in user_targets:
        MonthlyTarget.objects.update_or_create(
            user=user_target.user,
            month=current_month,
            year=current_year,
            defaults={'target_amount': user_target.target}
        )
        count += 1
    
    return f"Recalculated monthly targets for {count} users for {current_month}/{current_year}"
