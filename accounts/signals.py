from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.utils import create_targets_for_financial_and_physical_year_for_user
from django.utils import timezone



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


@receiver(post_save, sender=User)
def record_user_active_change(sender, instance, created, **kwargs):
    """Record changes to `User.is_active` into `UserActiveHistory`.

    We only create a new history row when the latest recorded value differs
    from the current `is_active` to avoid duplicate rows on unrelated saves.
    """
    try:
        from accounts.models import UserActiveHistory
    except Exception:
        return

    # Get latest history entry for this user
    last = UserActiveHistory.objects.filter(user=instance).order_by('-changed_at').first()
    if not last or last.is_active != instance.is_active:
        try:
            UserActiveHistory.objects.create(
                user=instance,
                is_active=instance.is_active,
                changed_at=timezone.now(),
            )
            # If the user was just re-activated, ensure they have MonthlyTarget rows
            # for the relevant financial/physical years so analytics include them.
            try:
                if not created and instance.is_active:
                    create_targets_for_financial_and_physical_year_for_user(user=instance)
            except Exception:
                # Non-fatal: don't block the user save if target creation fails
                pass
        except Exception:
            # avoid breaking user save if history creation fails
            pass
