from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_q.tasks import schedule, Schedule


class Command(BaseCommand):
    help = "Schedules monthly target creation and adjustment tasks (using Django-Q)."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Recreate schedules if they already exist')
        parser.add_argument('--list', action='store_true', help='List existing schedules only')

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()
        now = timezone.now()

        if options['list']:
            self._list_schedules()
            return

        # Calculate month boundaries
        first_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day_this_month = first_next_month - timedelta(days=1)

        # Month start & end run times
        month_start = datetime.combine(first_next_month, time(0, 10)).astimezone(tz)
        month_end = datetime.combine(last_day_this_month, time(23, 59)).astimezone(tz)

        # Calculate next financial year start (April 1st)
        current_year = now.year
        if now.month >= 4:  # If we're in Apr-Dec, next financial year is next calendar year
            next_financial_year = current_year + 1
        else:  # If we're in Jan-Mar, next financial year is this calendar year
            next_financial_year = current_year
        financial_year_start = datetime.combine(
            datetime(next_financial_year, 4, 1).date(), 
            time(1, 0)
        ).astimezone(tz)

        # Calculate next physical year start (January 1st)
        next_physical_year = current_year + 1
        physical_year_start = datetime.combine(
            datetime(next_physical_year, 1, 1).date(), 
            time(1, 0)
        ).astimezone(tz)

        tasks = [
            {
                "name": "create_monthly_targets_for_all_users",
                "task": "accounts.tasks.create_monthly_targets_for_all_users",
                "next_run": month_start,
                "schedule_type": Schedule.MONTHLY,
                "repeats": -1,
                "months": 1,
            },
            {
                "name": "adjust_monthly_targets",
                "task": "accounts.tasks.adjust_monthly_targets",
                "next_run": month_end,
                "schedule_type": Schedule.MONTHLY,
                "repeats": -1,
                "months": 1,
            },
            {
                "name": "create_targets_financial_year_start",
                "task": "accounts.tasks.create_targets_from_start_to_current",
                "next_run": financial_year_start,
                "schedule_type": Schedule.YEARLY,
                "repeats": -1,
                "months": 12,
            },
            {
                "name": "create_targets_physical_year_start",
                "task": "accounts.tasks.create_targets_from_start_to_current",
                "next_run": physical_year_start,
                "schedule_type": Schedule.YEARLY,
                "repeats": -1,
                "months": 12,
            },
        ]

        for t in tasks:
            self._create_or_update_schedule(t, options['force'])

    def _create_or_update_schedule(self, task_info, force):
        existing = Schedule.objects.filter(name=task_info['name']).first()

        if existing and not force:
            self.stdout.write(self.style.WARNING(f"📋 {task_info['name']} already exists (ID: {existing.id})"))
            return

        if existing and force:
            existing.delete()
            self.stdout.write(self.style.WARNING(f"🗑️ Recreating {task_info['name']}..."))

        try:
            sched = schedule(
                task_info['task'],
                name=task_info['name'],
                schedule_type=task_info['schedule_type'],
                months=task_info['months'],
                repeats=task_info['repeats'],
                next_run=task_info['next_run'],
            )
            schedule_type_name = "MONTHLY" if task_info['schedule_type'] == Schedule.MONTHLY else "YEARLY"
            self.stdout.write(self.style.SUCCESS(
                f"✅ Scheduled ({schedule_type_name}): {task_info['name']} → {task_info['next_run']}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error scheduling {task_info['name']}: {e}"))

    def _list_schedules(self):
        schedules = Schedule.objects.all().order_by('name')
        if not schedules.exists():
            self.stdout.write(self.style.WARNING("⚠️ No schedules found"))
            return
        self.stdout.write(self.style.SUCCESS("📋 Existing Django-Q schedules:"))
        for s in schedules:
            schedule_type = "MONTHLY" if s.schedule_type == Schedule.MONTHLY else "YEARLY"
            self.stdout.write(f" - {s.name} ({schedule_type}) | Next run: {s.next_run}")
