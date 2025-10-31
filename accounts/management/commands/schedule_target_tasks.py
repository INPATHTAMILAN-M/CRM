"""
Management command to schedule monthly target adjustment tasks with Django-Q
"""
from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = 'Schedule monthly target adjustment tasks with Django-Q'

    def handle(self, *args, **options):
        # Schedule monthly target adjustment to run at the end of each month
        schedule, created = Schedule.objects.update_or_create(
            name='adjust_monthly_targets',
            defaults={
                'func': 'accounts.tasks.adjust_monthly_targets',
                'schedule_type': Schedule.MINUTES,
                'next_run': None,  # Will be calculated automatically
                'repeats': -1,  # Repeat indefinitely
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created schedule for adjust_monthly_targets'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Updated existing schedule for adjust_monthly_targets'
                )
            )
        
        # You can also schedule a daily recalculation if needed
        schedule2, created2 = Schedule.objects.update_or_create(
            name='recalculate_all_monthly_targets',
            defaults={
                'func': 'accounts.tasks.recalculate_all_monthly_targets',
                'schedule_type': Schedule.DAILY,
                'next_run': None,
                'repeats': -1,
            }
        )
        
        if created2:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created schedule for recalculate_all_monthly_targets'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Updated existing schedule for recalculate_all_monthly_targets'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nSchedules created! Make sure Django-Q cluster is running:\n'
                'python manage.py qcluster'
            )
        )
