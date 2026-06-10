from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from datetime import datetime
from dateutil.relativedelta import relativedelta

from accounts.models import MonthlyTarget, UserTarget
from accounts.tasks import calculate_user_achieved_amount


class Command(BaseCommand):
    help = "Rebuild monthly targets for a user over a date range, applying carryover logic deterministically."

    def add_arguments(self, parser):
        parser.add_argument('--user', type=int, required=True, help='User id')
        parser.add_argument('--start', type=str, required=True, help='Start month in YYYY-MM')
        parser.add_argument('--end', type=str, required=True, help='End month in YYYY-MM')

    def handle(self, *args, **options):
        user_id = options['user']
        try:
            start = datetime.strptime(options['start'], '%Y-%m')
            end = datetime.strptime(options['end'], '%Y-%m')
        except ValueError:
            raise CommandError('Start and end must be in YYYY-MM format')

        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise CommandError(f'User {user_id} not found')

        base_target = None
        ut = UserTarget.objects.filter(user=user).first()
        if ut:
            base_target = ut.target

        cur = start.replace(day=1)
        prev_remaining = None

        while cur <= end.replace(day=1):
            month = cur.month
            year = cur.year

            mt = MonthlyTarget.objects.filter(user=user, month=month, year=year).first()
            if not mt:
                # create with base target if available
                mt = MonthlyTarget.objects.create(user=user, month=month, year=year, target_amount=(base_target or 0))

            achieved = calculate_user_achieved_amount(user, month, year)
            # current remaining = mt.target_amount - achieved
            remaining = (mt.target_amount or 0) - achieved

            self.stdout.write(f'{user.username} {month}/{year}: target={mt.target_amount} achieved={achieved} remaining={remaining}')

            # prepare next month's target
            next_month = (cur + relativedelta(months=1)).replace(day=1)
            if next_month <= end.replace(day=1):
                # compute next target relative to base_target
                if base_target is None:
                    # fallback to using current next month's existing or mt.target_amount
                    next_mt, _ = MonthlyTarget.objects.get_or_create(user=user, month=next_month.month, year=next_month.year,
                                                                     defaults={'target_amount': mt.target_amount})
                else:
                    if remaining > 0:
                        next_target = base_target + remaining
                    else:
                        next_target = max(base_target - abs(remaining), 0)
                    next_mt, _ = MonthlyTarget.objects.get_or_create(user=user, month=next_month.month, year=next_month.year,
                                                                     defaults={'target_amount': next_target})
                    # update if exists but different
                    if next_mt.target_amount != next_target:
                        next_mt.target_amount = next_target
                        next_mt.save()

            cur = cur + relativedelta(months=1)

        self.stdout.write(self.style.SUCCESS('Rebuild complete'))
