from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission

SOURCE_DB = 'default'
TARGET_DB = 'mysql'


class Command(BaseCommand):
    help = 'Sync User.groups, User.user_permissions, and Group.permissions from default to mysql'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Syncing M2M fields for User and Group...")

        # Sync User.groups and User.user_permissions
        for user in User.objects.using(SOURCE_DB).all():
            try:
                dest_user = User.objects.using(TARGET_DB).get(username=user.username)

                # Sync groups
                group_ids = list(user.groups.using(SOURCE_DB).values_list('id', flat=True))
                groups = Group.objects.using(TARGET_DB).filter(id__in=group_ids)
                dest_user.groups.set(groups)

                # Sync user_permissions
                perm_ids = list(user.user_permissions.using(SOURCE_DB).values_list('id', flat=True))
                perms = Permission.objects.using(TARGET_DB).filter(id__in=perm_ids)
                dest_user.user_permissions.set(perms)

                self.stdout.write(f"✅ Synced M2M for user: {user.username}")
            except Exception as e:
                self.stderr.write(f"❌ Failed syncing user {user.username}: {e}")

        # Sync Group.permissions
        for group in Group.objects.using(SOURCE_DB).all():
            try:
                dest_group = Group.objects.using(TARGET_DB).get(name=group.name)

                perm_ids = list(group.permissions.using(SOURCE_DB).values_list('id', flat=True))
                perms = Permission.objects.using(TARGET_DB).filter(id__in=perm_ids)
                dest_group.permissions.set(perms)

                self.stdout.write(f"✅ Synced permissions for group: {group.name}")
            except Exception as e:
                self.stderr.write(f"❌ Failed syncing group {group.name}: {e}")

        self.stdout.write("✅ Sync complete.")
