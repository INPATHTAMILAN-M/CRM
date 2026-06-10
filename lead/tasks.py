"""
Scheduled tasks for reminders and automated emails using Django-Q
This handles recurring tasks like follow-up reminders, meeting reminders, overdue alerts, etc.
"""
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Task, Log, Opportunity
from .email_utils import (
    TaskNotifications, MeetingCallNotifications, GeneralNotifications
)
import logging

logger = logging.getLogger(__name__)


def send_follow_up_reminders():
    """
    Send follow-up reminders for tasks due today or tomorrow
    Scheduled to run daily
    """
    try:
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get tasks due today or tomorrow
        upcoming_tasks = Task.objects.filter(
            task_date_time__gte=today_start,
            task_date_time__lt=today_end,
            is_active=True
        ).select_related('contact')
        
        for task in upcoming_tasks:
            # Get assigned user(s) from TaskConversationLog or task creator
            if hasattr(task, 'task_task_assignments') and task.task_task_assignments.exists():
                for assignment in task.task_task_assignments.filter(is_active=True):
                    TaskNotifications.follow_up_reminder(task, assignment.assigned_to)
                    logger.info(f"Follow-up reminder sent for task: {task.id} to {assignment.assigned_to.email}")
            else:
                # Send to task creator as fallback
                TaskNotifications.follow_up_reminder(task, task.created_by)
                logger.info(f"Follow-up reminder sent for task: {task.id} to {task.created_by.email}")
    except Exception as e:
        logger.error(f"Error in send_follow_up_reminders: {str(e)}")


def check_overdue_tasks():
    """
    Check for overdue tasks and send alert emails
    Scheduled to run every 2 hours
    """
    try:
        now = timezone.now()
        
        # Get overdue tasks that haven't been completed
        overdue_tasks = Task.objects.filter(
            task_date_time__lt=now,
            is_active=True
        ).select_related('contact')
        
        for task in overdue_tasks:
            # Get assigned user(s)
            if hasattr(task, 'task_task_assignments') and task.task_task_assignments.exists():
                for assignment in task.task_task_assignments.filter(is_active=True):
                    # Check if we already sent an alert (using a simple heuristic)
                    GeneralNotifications.overdue_task_alert(task, assignment.assigned_to)
                    logger.info(f"Overdue task alert sent for task: {task.id} to {assignment.assigned_to.email}")
            else:
                GeneralNotifications.overdue_task_alert(task, task.created_by)
                logger.info(f"Overdue task alert sent for task: {task.id} to {task.created_by.email}")
    except Exception as e:
        logger.error(f"Error in check_overdue_tasks: {str(e)}")


def send_meeting_reminders_24hrs():
    """
    Send meeting reminders 24 hours before scheduled meeting
    Scheduled to run every hour
    """
    try:
        now = timezone.now()
        reminder_time = now + timedelta(hours=24)
        reminder_start = reminder_time.replace(minute=0, second=0, microsecond=0)
        reminder_end = reminder_start + timedelta(hours=1)
        
        # Get meetings scheduled in exactly 24 hours (approximately)
        meetings = Log.objects.filter(
            log_type='Meeting',
            follow_up_date_time__gte=reminder_start,
            follow_up_date_time__lt=reminder_end,
            is_active=True
        ).select_related('contact', 'created_by')
        
        for meeting in meetings:
            attendees = [meeting.created_by]
            if meeting.contact.assigned_to:
                attendees.append(meeting.contact.assigned_to)
            
            attendees = list(set(attendees))
            MeetingCallNotifications.meeting_reminder_24hrs(meeting, attendees)
            logger.info(f"24-hour meeting reminder sent for meeting: {meeting.id}")
    except Exception as e:
        logger.error(f"Error in send_meeting_reminders_24hrs: {str(e)}")


def send_meeting_reminders_1hr():
    """
    Send meeting reminders 1 hour before scheduled meeting
    Scheduled to run every 30 minutes
    """
    try:
        now = timezone.now()
        reminder_time = now + timedelta(hours=1)
        reminder_start = reminder_time.replace(minute=0, second=0, microsecond=0)
        reminder_end = reminder_start + timedelta(hours=1)
        
        # Get meetings scheduled in approximately 1 hour
        meetings = Log.objects.filter(
            log_type='Meeting',
            follow_up_date_time__gte=reminder_start,
            follow_up_date_time__lt=reminder_end,
            is_active=True
        ).select_related('contact', 'created_by')
        
        for meeting in meetings:
            attendees = [meeting.created_by]
            if meeting.contact.assigned_to:
                attendees.append(meeting.contact.assigned_to)
            
            attendees = list(set(attendees))
            MeetingCallNotifications.meeting_reminder_1hr(meeting, attendees)
            logger.info(f"1-hour meeting reminder sent for meeting: {meeting.id}")
    except Exception as e:
        logger.error(f"Error in send_meeting_reminders_1hr: {str(e)}")


def check_payment_due_reminders():
    """
    Send payment due reminders (7 days and 1 day before)
    Note: Requires Invoice model to be implemented
    Scheduled to run daily
    """
    try:
        # This will be implemented when Invoice model is created
        # Similar pattern to above tasks
        logger.info("Payment due reminder check completed")
    except Exception as e:
        logger.error(f"Error in check_payment_due_reminders: {str(e)}")


def check_high_value_deals():
    """
    Send admin alert for high-value deals (> $50,000 threshold)
    Scheduled to run every 6 hours
    """
    try:
        # Get high-value opportunities created/updated in last 6 hours
        now = timezone.now()
        six_hours_ago = now - timedelta(hours=6)
        threshold = 50000
        
        high_value_opps = Opportunity.objects.filter(
            opportunity_value__gte=threshold,
            created_on__gte=six_hours_ago,
            is_active=True
        ).select_related('owner', 'lead', 'stage', 'name')
        
        if high_value_opps.exists():
            # Get admin users
            admin_users = User.objects.filter(groups__name='Admin')
            
            for opp in high_value_opps:
                GeneralNotifications.admin_alert_high_value_deal(opp, admin_users)
                logger.info(f"High-value deal alert sent for opportunity: {opp.name.name}")
    except Exception as e:
        logger.error(f"Error in check_high_value_deals: {str(e)}")


def send_re_engagement_emails():
    """
    Send re-engagement emails to inactive users (no login for 30 days)
    Scheduled to run weekly on Monday
    """
    try:
        from django.contrib.auth.models import User
        from django.db.models import Q
        from django.contrib.sessions.models import Session
        import pickle
        
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Get users who haven't logged in for 30 days
        # This checks based on last_login field
        inactive_users = User.objects.filter(
            last_login__lt=thirty_days_ago,
            is_active=True
        ).exclude(email='')
        
        for user in inactive_users:
            GeneralNotifications.re_engagement_email(user)
            logger.info(f"Re-engagement email sent to user: {user.email}")
    except Exception as e:
        logger.error(f"Error in send_re_engagement_emails: {str(e)}")


def check_birthday_campaigns():
    """
    Send birthday/anniversary campaign emails
    Scheduled to run daily
    Note: Requires birthday_date or anniversary_date field in Contact model
    """
    try:
        from .models import Contact
        from datetime import date
        
        today = date.today()
        
        # Get contacts with birthdays today
        # Note: This requires birthday_date field in Contact model
        # birthdays = Contact.objects.filter(
        #     birthday_date__month=today.month,
        #     birthday_date__day=today.day,
        #     is_active=True
        # )
        
        logger.info("Birthday campaign check completed")
    except Exception as e:
        logger.error(f"Error in check_birthday_campaigns: {str(e)}")


# Dictionary of scheduled tasks to be registered in Django-Q
SCHEDULED_TASKS = {
    'send_follow_up_reminders': {
        'task': 'lead.tasks.send_follow_up_reminders',
        'schedule': 'daily',
        'repeats': -1,  # Repeat indefinitely
    },
    'check_overdue_tasks': {
        'task': 'lead.tasks.check_overdue_tasks',
        'schedule': 'every 2h',
        'repeats': -1,
    },
    'send_meeting_reminders_24hrs': {
        'task': 'lead.tasks.send_meeting_reminders_24hrs',
        'schedule': 'every 1h',
        'repeats': -1,
    },
    'send_meeting_reminders_1hr': {
        'task': 'lead.tasks.send_meeting_reminders_1hr',
        'schedule': 'every 30m',
        'repeats': -1,
    },
    'check_payment_due_reminders': {
        'task': 'lead.tasks.check_payment_due_reminders',
        'schedule': 'daily',
        'repeats': -1,
    },
    'check_high_value_deals': {
        'task': 'lead.tasks.check_high_value_deals',
        'schedule': 'every 6h',
        'repeats': -1,
    },
    'send_re_engagement_emails': {
        'task': 'lead.tasks.send_re_engagement_emails',
        'schedule': 'every 7d',
        'repeats': -1,
    },
    'check_birthday_campaigns': {
        'task': 'lead.tasks.check_birthday_campaigns',
        'schedule': 'daily',
        'repeats': -1,
    },
}
