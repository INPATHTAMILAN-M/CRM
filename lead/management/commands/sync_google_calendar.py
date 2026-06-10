from django.core.management.base import BaseCommand

from lead.google_calendar import sync_google_events


class Command(BaseCommand):
    help = 'Sync tasks from Google Calendar events into the local Task database.'

    def handle(self, *args, **options):
        try:
            count = sync_google_events()
            self.stdout.write(self.style.SUCCESS(f'Successfully synced {count} tasks from Google Calendar.'))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Error syncing Google Calendar: {exc}'))
            raise
