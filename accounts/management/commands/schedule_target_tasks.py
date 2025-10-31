"""
Management command to schedule monthly target adjustment tasks with Django-Q
"""
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.tasks import schedule, Schedule


class Command(BaseCommand):
    help = 'Schedule monthly target adjustment tasks with Django-Q'

    def handle(self, *args, **options):
        now = timezone.now()
        # Get first day of next month at 00:00
        first_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_run_time = datetime.combine(first_next_month, time.min).astimezone(
            timezone.get_current_timezone()
        )

        result = schedule(
            'accounts.tasks.adjust_monthly_targets',
            name='adjust_monthly_targets',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=next_run_time
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully scheduled adjust_monthly_targets (ID: {result.id})'
            )
        )
