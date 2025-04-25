from django.core.management.base import BaseCommand
from accounts.models import Teams
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Migrate Teams data from mysql (SQLite) to default (MySQL) without creating any users.'

    def handle(self, *args, **kwargs):
        source_teams = Teams.objects.using('mysql').all()
        print(f"🔄 Migrating {source_teams.count()} teams from mysql to default...")
        migrated = 0
        skipped = 0

        for team in source_teams:
            try:
                bdm_user = User.objects.using('default').get(username=team.bdm_user.username)

                new_team = Teams.objects.using('default').create(bdm_user=bdm_user)

                for bde_user in team.bde_user.all():
                    bde = User.objects.using('default').get(username=bde_user.username)
                    new_team.bde_user.add(bde)

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Migrated: BDM {bdm_user.username}"
                ))
                migrated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"❌ Skipped team under BDM {team.bdm_user.username}: {e}"
                ))
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Completed. Migrated: {migrated}, Skipped: {skipped}"))
