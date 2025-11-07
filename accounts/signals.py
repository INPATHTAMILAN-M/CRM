from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.utils import create_targets_for_financial_and_physical_year_for_user


@receiver(post_save, sender=User)
def create_user_targets_on_user_creation(sender, instance, created, **kwargs):
    """
    Automatically create targets for new users when they are created.
    This runs after a User instance is saved.
    """
    if created:  # Only run for newly created users
        print(f"🆕 New user created: {instance.username}")
        try:
            # Create targets for the user
            create_targets_for_financial_and_physical_year_for_user(
                user=instance,
                # These will default to current financial/physical years
                # You can override these parameters if needed
            )
            print(f"✅ Successfully created targets for user: {instance.username}")
        except Exception as e:
            print(f"❌ Error creating targets for user {instance.username}: {e}")
