from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.tasks import schedule, Schedule


class Command(BaseCommand):
    help = 'Schedule monthly target creation and adjustment tasks with Django-Q'

    def handle(self, *args, **options):
        now = timezone.now()
        tz = timezone.get_current_timezone()

        # --- Common next run time: first day of next month at 00:00 ---
        first_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)

        # Task 1: Create monthly targets at 00:00
        create_time = datetime.combine(first_next_month, time(0, 0)).astimezone(tz)

        # Task 2: Adjust monthly targets 10 minutes later (00:10)
        adjust_time = datetime.combine(first_next_month, time(0, 10)).astimezone(tz)

        # --- Schedule 1 ---
        result1 = schedule(
            'accounts.tasks.create_monthly_targets_for_all_users',
            name='create_monthly_targets_for_all_users',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=create_time
        )

        # --- Schedule 2 ---
        result2 = schedule(
            'accounts.tasks.adjust_monthly_targets',
            name='adjust_monthly_targets',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=adjust_time
        )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully scheduled:\n'
            f'  1️⃣ create_monthly_targets_for_all_users (ID: {result1.id}) at {create_time}\n'
            f'  2️⃣ adjust_monthly_targets (ID: {result2.id}) at {adjust_time}'
        ))
