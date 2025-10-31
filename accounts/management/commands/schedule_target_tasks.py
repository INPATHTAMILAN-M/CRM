"""
Management command to schedule monthly target adjustment tasks with Django-Q
"""
from django.core.management.base import BaseCommand
from django_q.tasks import schedule, Schedule


class Command(BaseCommand):
    help = 'Schedule monthly target adjustment tasks with Django-Q'

    def handle(self, *args, **options):
        # Schedule monthly target adjustment to run every minute
        result = schedule(
            'accounts.tasks.adjust_monthly_targets',
            name='adjust_monthly_targets',
            schedule_type=Schedule.MONTHLY, # I = minutes
            months=1,
            repeats=-1  # Repeat indefinitely
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully scheduled adjust_monthly_targets (ID: {result})'
            )
        )
        
        
