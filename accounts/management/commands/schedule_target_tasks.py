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
            schedule_type=Schedule.MINUTES, # I = minutes
            minutes=1,
            repeats=-1  # Repeat indefinitely
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully scheduled adjust_monthly_targets (ID: {result})'
            )
        )
        
        # # Schedule daily recalculation
        # result2 = schedule(
        #     'accounts.tasks.recalculate_all_monthly_targets',
        #     name='recalculate_all_monthly_targets',
        #     schedule_type=Schedule.DAILY,
        #     minutes=1440,
        #     repeats=-1
        # )
        
        # self.stdout.write(
        #     self.style.SUCCESS(
        #         f'Successfully scheduled recalculate_all_monthly_targets (ID: {result2})'
        #     )
        # )
        
        # self.stdout.write(
        #     self.style.SUCCESS(
        #         '\nSchedules created! Make sure Django-Q cluster is running:\n'
        #         'python manage.py qcluster'
        #     )
        # )
