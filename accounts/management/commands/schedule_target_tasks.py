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

        tasks = [
            {
                "name": "create_monthly_targets_for_all_users",
                "task": "accounts.tasks.create_monthly_targets_for_all_users",
                "next_run": month_start,
            },
            {
                "name": "adjust_monthly_targets",
                "task": "accounts.tasks.adjust_monthly_targets",
                "next_run": month_end,
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
                schedule_type=Schedule.MONTHLY,
                months=1,
                repeats=-1,
                next_run=task_info['next_run'],
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Scheduled: {task_info['name']} → {task_info['next_run']}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error scheduling {task_info['name']}: {e}"))

    def _list_schedules(self):
        schedules = Schedule.objects.all().order_by('name')
        if not schedules.exists():
            self.stdout.write(self.style.WARNING("⚠️ No schedules found"))
            return
        self.stdout.write(self.style.SUCCESS("📋 Existing Django-Q schedules:"))
        for s in schedules:
            self.stdout.write(f" - {s.name} | Next run: {s.next_run}")
