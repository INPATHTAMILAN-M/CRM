from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections
from django.contrib.auth.models import User, Group, Permission

# List of date/datetime fields you want to preserve values for
AUTO_FIELDS = ['created_on', 'updated_on', 'assigned_on', 'date', 'note_on', 'created_at']

TARGET_DB = 'mysql'  # your MySQL DB alias

def disable_foreign_key_checks(using=TARGET_DB):
    with connections[using].cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')

def enable_foreign_key_checks(using=TARGET_DB):
    with connections[using].cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS=1;')

def patch_auto_fields(model, enable=False):
    for field_name in AUTO_FIELDS:
        try:
            field = model._meta.get_field(field_name)
            if hasattr(field, 'auto_now'):
                field.auto_now = enable
            if hasattr(field, 'auto_now_add'):
                field.auto_now_add = enable
        except Exception:
            pass  # Field does not exist

def clone_model_data(model, using_src='default', using_dest=TARGET_DB):
    objects = list(model.objects.using(using_src).all())
    if not objects:
        return

    patch_auto_fields(model, enable=False)
    model.objects.using(using_dest).bulk_create(objects, ignore_conflicts=True)
    patch_auto_fields(model, enable=True)

    print(f"✔️ Cloned {model.__name__} ({len(objects)} records)")

class Command(BaseCommand):
    help = f'Clone data from "default" to "{TARGET_DB}"'

    def handle(self, *args, **kwargs):
        self.stdout.write(f"🔄 Cloning from 'default' to '{TARGET_DB}'...")

        disable_foreign_key_checks(TARGET_DB)

        for model in [Permission, Group, User]:
            try:
                clone_model_data(model)
            except Exception as e:
                self.stderr.write(f"❌ Failed cloning {model.__name__}: {e}")

        excluded_apps = ['admin', 'sessions', 'contenttypes']
        excluded_models = ['LogEntry']

        for model in apps.get_models():
            app_label = model._meta.app_label
            model_name = model.__name__

            if app_label in excluded_apps or model_name in excluded_models:
                continue

            if model in [User, Group, Permission]:
                continue

            try:
                clone_model_data(model)
            except Exception as e:
                self.stderr.write(f"⚠️ Skipped {model.__name__} due to: {e}")

        enable_foreign_key_checks(TARGET_DB)
        self.stdout.write("✅ Clone completed successfully.")
