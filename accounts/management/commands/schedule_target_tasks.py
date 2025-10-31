from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.tasks import schedule, Schedule


class Command(BaseCommand):
    help = 'Schedules monthly target creation (month end) and adjustment (month start) tasks with Django-Q.'

    def handle(self, *args, **options):
        now = timezone.now()
        tz = timezone.get_current_timezone()

        # ----------------------------
        # Calculate key dates
        # ----------------------------
        first_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day_this_month = first_next_month - timedelta(days=1)

        # Month-end: last day of this month at 23:59
        month_end_time = datetime.combine(last_day_this_month, time(23, 59)).astimezone(tz)

        # Month-start: first day of next month at 00:10
        month_start_time = datetime.combine(first_next_month, time(0, 10)).astimezone(tz)

        # ----------------------------
        # 1️⃣ Schedule: create targets at end of the month
        # ----------------------------
        result1 = schedule(
            'accounts.tasks.create_monthly_targets_for_all_users',
            name='create_monthly_targets_for_all_users',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=month_start_time
        )

        # ----------------------------
        # 2️⃣ Schedule: adjust targets at start of next month
        # ----------------------------
        result2 = schedule(
            'accounts.tasks.adjust_monthly_targets',
            name='adjust_monthly_targets',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=month_end_time
        )

        # ----------------------------
        # ✅ Output results
        # ----------------------------
        self.stdout.write(
            self.style.SUCCESS(
                f"""
Successfully scheduled monthly tasks:

🕛 1️⃣ create_monthly_targets_for_all_users
    - Runs at end of month: {month_end_time}
    - Schedule ID: {result1.id}

🕐 2️⃣ adjust_monthly_targets
    - Runs at start of month: {month_start_time}
    - Schedule ID: {result2.id}
"""
            )
        )
