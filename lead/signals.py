"""
Django signals for lead and opportunity notifications
Automatically sends emails when models are created/updated
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import (
    Lead, Opportunity, Task, Task_Assignment, Log, Notification, Lead_Assignment
)
from .email_utils import (
    LeadNotifications, OpportunityNotifications, TaskNotifications, 
    MeetingCallNotifications, GeneralNotifications
)
import logging

logger = logging.getLogger(__name__)


# Store original values to detect changes
_lead_status_changes = {}


@receiver(pre_save, sender=Lead)
def track_lead_status_change(sender, instance, **kwargs):
    """Track lead status changes before save"""
    try:
        if instance.pk:
            old_instance = Lead.objects.get(pk=instance.pk)
            _lead_status_changes[instance.pk] = {
                'old_status': old_instance.lead_status,
                'changed_by': None  # Will be set in view
            }
    except Lead.DoesNotExist:
        pass


@receiver(post_save, sender=Lead)
def handle_lead_created_or_updated(sender, instance, created, **kwargs):
    """Send notifications when lead is created or updated"""
    try:
        if created:
            # Send new lead created notification
            LeadNotifications.new_lead_created(instance)
            logger.info(f"New lead notification sent for lead: {instance.name}")
        else:
            # Check if status changed
            if instance.pk in _lead_status_changes:
                old_status = _lead_status_changes[instance.pk]['old_status']
                if old_status != instance.lead_status:
                    # Status has changed, send notification
                    LeadNotifications.lead_status_changed(
                        instance,
                        old_status.name if old_status else 'Not Set',
                        instance.lead_status.name if instance.lead_status else 'Not Set',
                        User.objects.first()  # Default user, ideally should be passed from view
                    )
                    logger.info(f"Lead status change notification sent for lead: {instance.name}")
                del _lead_status_changes[instance.pk]
    except Exception as e:
        logger.error(f"Error in handle_lead_created_or_updated: {str(e)}")


@receiver(post_save, sender=Lead_Assignment)
def handle_lead_assignment(sender, instance, created, **kwargs):
    """Send notification when lead is assigned"""
    try:
        if created:
            LeadNotifications.lead_assigned(
                instance.lead,
                instance.assigned_to,
                instance.assigned_by
            )
            logger.info(f"Lead assignment notification sent for: {instance.lead.name} -> {instance.assigned_to.username}")
    except Exception as e:
        logger.error(f"Error in handle_lead_assignment: {str(e)}")


# Store original opportunity stage
_opportunity_stage_changes = {}


@receiver(pre_save, sender=Opportunity)
def track_opportunity_stage_change(sender, instance, **kwargs):
    """Track opportunity stage changes before save"""
    try:
        if instance.pk:
            old_instance = Opportunity.objects.get(pk=instance.pk)
            _opportunity_stage_changes[instance.pk] = {
                'old_stage': old_instance.stage
            }
    except Opportunity.DoesNotExist:
        pass


@receiver(post_save, sender=Opportunity)
def handle_opportunity_created_or_updated(sender, instance, created, **kwargs):
    """Send notifications when opportunity is created or updated"""
    try:
        if created:
            # Send new opportunity created notification
            OpportunityNotifications.opportunity_created(instance)
            logger.info(f"New opportunity notification sent for: {instance.name.name}")
        else:
            # Check if stage changed
            if instance.pk in _opportunity_stage_changes:
                old_stage = _opportunity_stage_changes[instance.pk]['old_stage']
                if old_stage != instance.stage:
                    # Stage has changed, send notification
                    OpportunityNotifications.opportunity_stage_changed(
                        instance,
                        old_stage.stage if old_stage else 'Not Set',
                        instance.stage.stage if instance.stage else 'Not Set',
                        User.objects.first()  # Default user
                    )
                    logger.info(f"Opportunity stage change notification sent for: {instance.name.name}")
                del _opportunity_stage_changes[instance.pk]
    except Exception as e:
        logger.error(f"Error in handle_opportunity_created_or_updated: {str(e)}")


@receiver(post_save, sender=Task_Assignment)
def handle_task_assignment(sender, instance, created, **kwargs):
    """Send notification when task is assigned"""
    try:
        if created:
            TaskNotifications.task_created(
                instance.task,
                instance.assigned_to,
                instance.assigned_by
            )
            logger.info(f"Task assignment notification sent for: {instance.assigned_to.username}")
    except Exception as e:
        logger.error(f"Error in handle_task_assignment: {str(e)}")


@receiver(post_save, sender=Log)
def handle_meeting_created(sender, instance, created, **kwargs):
    """Send notification when meeting/call is logged"""
    try:
        if created and instance.log_type in ['Meeting', 'Call']:
            # Get all assigned users for this contact
            contact = instance.contact
            attendees = [instance.created_by]
            
            # Add contact's assigned user if exists
            if contact.assigned_to:
                attendees.append(contact.assigned_to)
            
            # Remove duplicates
            attendees = list(set(attendees))
            
            if instance.log_type == 'Meeting':
                MeetingCallNotifications.meeting_scheduled(instance, attendees)
                logger.info(f"Meeting scheduled notification sent for contact: {contact.name}")
            
    except Exception as e:
        logger.error(f"Error in handle_meeting_created: {str(e)}")


# Ready signal handlers
def ready():
    """
    This function will be called when the app is ready.
    All signal handlers will be imported and registered here.
    """
    pass
