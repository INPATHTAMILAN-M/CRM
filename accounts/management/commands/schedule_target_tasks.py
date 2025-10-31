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
        # 1️⃣ Month-end schedule (create targets)
        # ----------------------------
        first_next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        last_day_this_month = first_next_month - timedelta(days=1)
        month_end_time = datetime.combine(last_day_this_month, time(23, 59)).astimezone(tz)

        result1 = schedule(
            'accounts.tasks.create_monthly_targets_for_all_users',
            name='create_monthly_targets_for_all_users',
            schedule_type=Schedule.MONTHLY,
            months=1,
            repeats=-1,
            next_run=month_start_time
        )

        first_day_next_month = first_next_month  # already calculated
        month_start_time = datetime.combine(first_day_next_month, time(0, 10)).astimezone(tz)

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
                f"""Successfully scheduled monthly tasks:

                        🕛 1️⃣ create_monthly_targets_for_all_users
                            - Runs at end of month: {month_end_time}
                            - Schedule ID: {result1.id}

                        🕐 2️⃣ adjust_monthly_targets
                            - Runs at start of month: {month_start_time}
                            - Schedule ID: {result2.id}
                """ ) 
                )
