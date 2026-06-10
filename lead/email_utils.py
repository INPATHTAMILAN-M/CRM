"""
Email utility functions and templates for CRM notifications
Handles all email communications for leads, opportunities, tasks, and reminders
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailNotification:
    """Base class for email notifications"""
    
    @staticmethod
    def send_email(subject, recipients, html_content=None, text_content=None, from_email=None):
        """
        Send email with both HTML and text versions
        
        Args:
            subject: Email subject
            recipients: List of email addresses
            html_content: HTML version of email
            text_content: Plain text version
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
        """
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        if not text_content and html_content:
            text_content = strip_tags(html_content)
        
        try:
            if html_content:
                msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
            else:
                send_mail(subject, text_content, from_email, recipients, fail_silently=False)
            logger.info(f"Email sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {str(e)}")
            return False


class LeadNotifications:
    """Email notifications for Lead model"""
    
    @staticmethod
    def new_lead_created(lead):
        """Notification when a new lead is created"""
        try:
            recipients = [lead.lead_owner.email]
            subject = f"🎯 New Lead Created: {lead.name}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>New Lead Created</h2>
                    <p>Hi <strong>{lead.lead_owner.first_name}</strong>,</p>
                    <p>A new lead has been created in the CRM system.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Lead Name:</strong> {lead.name}</p>
                        <p><strong>Country:</strong> {lead.country.name if lead.country else 'N/A'}</p>
                        <p><strong>Focus Segment:</strong> {lead.focus_segment.name if lead.focus_segment else 'N/A'}</p>
                        <p><strong>Lead Source:</strong> {lead.lead_source.source if lead.lead_source else 'N/A'}</p>
                        <p><strong>Created By:</strong> {lead.created_by.first_name} {lead.created_by.last_name}</p>
                        <p><strong>Created On:</strong> {lead.created_on.strftime('%d-%b-%Y %I:%M %p')}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/leads/{lead.id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Lead Details</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending new lead notification: {str(e)}")
            return False
    
    @staticmethod
    def lead_assigned(lead, assigned_to_user, assigned_by_user):
        """Notification when a lead is assigned to a user"""
        try:
            recipients = [assigned_to_user.email]
            subject = f"📌 Lead Assigned to You: {lead.name}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Lead Assigned</h2>
                    <p>Hi <strong>{assigned_to_user.first_name}</strong>,</p>
                    <p>A lead has been assigned to you by <strong>{assigned_by_user.first_name} {assigned_by_user.last_name}</strong>.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Lead Name:</strong> {lead.name}</p>
                        <p><strong>Lead Owner:</strong> {lead.lead_owner.first_name} {lead.lead_owner.last_name}</p>
                        <p><strong>Focus Segment:</strong> {lead.focus_segment.name if lead.focus_segment else 'N/A'}</p>
                        <p><strong>Lead Source:</strong> {lead.lead_source.source if lead.lead_source else 'N/A'}</p>
                        <p><strong>Company Website:</strong> {lead.company_website if lead.company_website else 'N/A'}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/leads/{lead.id}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Lead Details</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending lead assignment notification: {str(e)}")
            return False
    
    @staticmethod
    def lead_status_changed(lead, old_status, new_status, changed_by_user):
        """Notification when lead status changes"""
        try:
            recipients = [lead.lead_owner.email, lead.assigned_to.email] if lead.assigned_to else [lead.lead_owner.email]
            recipients = list(set(recipients))  # Remove duplicates
            
            subject = f"🔄 Lead Status Changed: {lead.name} - {new_status}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Lead Status Changed</h2>
                    <p>Hi,</p>
                    <p>The status of lead <strong>{lead.name}</strong> has been changed.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Lead Name:</strong> {lead.name}</p>
                        <p><strong>Previous Status:</strong> <span style="color: #dc3545;">{old_status}</span></p>
                        <p><strong>New Status:</strong> <span style="color: #28a745;">{new_status}</span></p>
                        <p><strong>Changed By:</strong> {changed_by_user.first_name} {changed_by_user.last_name}</p>
                        <p><strong>Changed On:</strong> {datetime.now().strftime('%d-%b-%Y %I:%M %p')}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/leads/{lead.id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Lead</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending lead status change notification: {str(e)}")
            return False


class OpportunityNotifications:
    """Email notifications for Opportunity model"""
    
    @staticmethod
    def opportunity_created(opportunity):
        """Notification when a new opportunity is created"""
        try:
            recipients = [opportunity.owner.email]
            if opportunity.lead and opportunity.lead.lead_owner.email not in recipients:
                recipients.append(opportunity.lead.lead_owner.email)
            
            subject = f"🎉 New Opportunity Created: {opportunity.name.name}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>New Opportunity Created</h2>
                    <p>Hi <strong>{opportunity.owner.first_name if opportunity.owner else 'User'}</strong>,</p>
                    <p>A new opportunity has been created.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Opportunity Name:</strong> {opportunity.name.name}</p>
                        <p><strong>Related Lead:</strong> {opportunity.lead.name if opportunity.lead else 'N/A'}</p>
                        <p><strong>Stage:</strong> {opportunity.stage.stage if opportunity.stage else 'N/A'}</p>
                        <p><strong>Value:</strong> {opportunity.opportunity_value if opportunity.opportunity_value else 'N/A'}</p>
                        <p><strong>Probability:</strong> {opportunity.probability_in_percentage}%</p>
                        <p><strong>Closing Date:</strong> {opportunity.closing_date.strftime('%d-%b-%Y') if opportunity.closing_date else 'N/A'}</p>
                        <p><strong>Created By:</strong> {opportunity.created_by.first_name} {opportunity.created_by.last_name}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/opportunities/{opportunity.id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Opportunity</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending opportunity creation notification: {str(e)}")
            return False
    
    @staticmethod
    def opportunity_stage_changed(opportunity, old_stage, new_stage, moved_by_user):
        """Notification when opportunity stage changes"""
        try:
            recipients = [opportunity.owner.email]
            if opportunity.lead and opportunity.lead.lead_owner.email not in recipients:
                recipients.append(opportunity.lead.lead_owner.email)
            
            subject = f"📈 Opportunity Stage Changed: {opportunity.name.name} - {new_stage}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Opportunity Stage Changed</h2>
                    <p>Hi,</p>
                    <p>The stage of opportunity <strong>{opportunity.name.name}</strong> has been updated.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Opportunity Name:</strong> {opportunity.name.name}</p>
                        <p><strong>Previous Stage:</strong> <span style="color: #dc3545;">{old_stage}</span></p>
                        <p><strong>New Stage:</strong> <span style="color: #28a745;">{new_stage}</span></p>
                        <p><strong>Probability:</strong> {opportunity.probability_in_percentage}%</p>
                        <p><strong>Value:</strong> {opportunity.opportunity_value if opportunity.opportunity_value else 'N/A'}</p>
                        <p><strong>Moved By:</strong> {moved_by_user.first_name} {moved_by_user.last_name}</p>
                        <p><strong>Moved On:</strong> {datetime.now().strftime('%d-%b-%Y %I:%M %p')}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/opportunities/{opportunity.id}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Opportunity</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending opportunity stage change notification: {str(e)}")
            return False


class TaskNotifications:
    """Email notifications for Task and follow-up reminders"""
    
    @staticmethod
    def task_created(task, assigned_to_user, assigned_by_user):
        """Notification when a task is assigned"""
        try:
            recipients = [assigned_to_user.email]
            subject = f"✅ New Task Assigned to You"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Task Assigned</h2>
                    <p>Hi <strong>{assigned_to_user.first_name}</strong>,</p>
                    <p>A new task has been assigned to you by <strong>{assigned_by_user.first_name} {assigned_by_user.last_name}</strong>.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Task Type:</strong> {task.task_type if task.task_type else 'General'}</p>
                        <p><strong>Contact:</strong> {task.contact.name if task.contact else 'N/A'}</p>
                        <p><strong>Task Detail:</strong> {task.task_detail if task.task_detail else 'No details provided'}</p>
                        <p><strong>Due Date:</strong> {task.task_date_time.strftime('%d-%b-%Y %I:%M %p') if task.task_date_time else 'Not set'}</p>
                        <p><strong>Created On:</strong> {task.created_on.strftime('%d-%b-%Y %I:%M %p')}</p>
                    </div>
                    
                    <p style="color: #dc3545;"><strong>⏰ Please complete this task on time.</strong></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending task assignment notification: {str(e)}")
            return False
    
    @staticmethod
    def follow_up_reminder(task, assigned_to_user):
        """Reminder email for upcoming follow-up"""
        try:
            recipients = [assigned_to_user.email]
            subject = f"⏰ Follow-up Reminder: {task.task_detail[:50] if task.task_detail else 'Task'}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Follow-up Reminder</h2>
                    <p>Hi <strong>{assigned_to_user.first_name}</strong>,</p>
                    <p>You have a follow-up task coming up!</p>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <p><strong>Task Type:</strong> {task.task_type if task.task_type else 'Follow-up'}</p>
                        <p><strong>Contact:</strong> {task.contact.name if task.contact else 'N/A'}</p>
                        <p><strong>Task Detail:</strong> {task.task_detail if task.task_detail else 'No details provided'}</p>
                        <p><strong>Due Date:</strong> {task.task_date_time.strftime('%d-%b-%Y %I:%M %p') if task.task_date_time else 'Not set'}</p>
                    </div>
                    
                    <p>Please ensure this is completed on time.</p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending follow-up reminder: {str(e)}")
            return False


class MeetingCallNotifications:
    """Email notifications for meetings and calls"""
    
    @staticmethod
    def meeting_scheduled(log, attendees):
        """Notification when a meeting is scheduled"""
        try:
            recipients = [user.email for user in attendees]
            subject = f"📅 Meeting Scheduled: {log.details[:50] if log.details else 'Meeting'}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Meeting Scheduled</h2>
                    <p>Hi,</p>
                    <p>A meeting has been scheduled.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Contact:</strong> {log.contact.name if log.contact else 'N/A'}</p>
                        <p><strong>Scheduled Date & Time:</strong> {log.follow_up_date_time.strftime('%d-%b-%Y %I:%M %p') if log.follow_up_date_time else 'Not set'}</p>
                        <p><strong>Meeting Details:</strong> {log.details if log.details else 'No details provided'}</p>
                        <p><strong>Created By:</strong> {log.created_by.first_name} {log.created_by.last_name}</p>
                    </div>
                    
                    <p><strong>📌 Please add this to your calendar.</strong></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending meeting scheduled notification: {str(e)}")
            return False
    
    @staticmethod
    def meeting_reminder_24hrs(log, attendees):
        """Reminder 24 hours before meeting"""
        try:
            recipients = [user.email for user in attendees]
            subject = f"🔔 Meeting Reminder (24 hours): {log.details[:50] if log.details else 'Meeting'}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Meeting Reminder - 24 Hours</h2>
                    <p>Hi,</p>
                    <p>Your meeting is scheduled in 24 hours!</p>
                    
                    <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196F3;">
                        <p><strong>Contact:</strong> {log.contact.name if log.contact else 'N/A'}</p>
                        <p><strong>Meeting Date & Time:</strong> {log.follow_up_date_time.strftime('%d-%b-%Y %I:%M %p') if log.follow_up_date_time else 'Not set'}</p>
                        <p><strong>Meeting Details:</strong> {log.details if log.details else 'No details provided'}</p>
                    </div>
                    
                    <p>Please prepare for this meeting.</p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending 24-hour meeting reminder: {str(e)}")
            return False
    
    @staticmethod
    def meeting_reminder_1hr(log, attendees):
        """Reminder 1 hour before meeting"""
        try:
            recipients = [user.email for user in attendees]
            subject = f"🚨 Meeting Reminder (1 hour): {log.details[:50] if log.details else 'Meeting'}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Meeting Reminder - 1 Hour</h2>
                    <p>Hi,</p>
                    <p>Your meeting is starting in 1 hour!</p>
                    
                    <div style="background-color: #ffe7e7; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <p><strong>Contact:</strong> {log.contact.name if log.contact else 'N/A'}</p>
                        <p><strong>Meeting Date & Time:</strong> {log.follow_up_date_time.strftime('%d-%b-%Y %I:%M %p') if log.follow_up_date_time else 'Not set'}</p>
                        <p><strong>Meeting Details:</strong> {log.details if log.details else 'No details provided'}</p>
                    </div>
                    
                    <p><strong>⏰ Please join the meeting immediately.</strong></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending 1-hour meeting reminder: {str(e)}")
            return False


class GeneralNotifications:
    """General email notifications for overdue tasks, inactive users, etc."""
    
    @staticmethod
    def overdue_task_alert(task, assigned_to_user):
        """Alert for overdue task"""
        try:
            recipients = [assigned_to_user.email]
            subject = f"⚠️ OVERDUE TASK: {task.task_detail[:50] if task.task_detail else 'Task'}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #dc3545;">⚠️ OVERDUE TASK</h2>
                    <p>Hi <strong>{assigned_to_user.first_name}</strong>,</p>
                    <p>The following task is overdue and requires immediate attention:</p>
                    
                    <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                        <p><strong>Task Type:</strong> {task.task_type if task.task_type else 'General'}</p>
                        <p><strong>Contact:</strong> {task.contact.name if task.contact else 'N/A'}</p>
                        <p><strong>Task Detail:</strong> {task.task_detail if task.task_detail else 'No details provided'}</p>
                        <p><strong>Due Date:</strong> {task.task_date_time.strftime('%d-%b-%Y %I:%M %p') if task.task_date_time else 'Not set'}</p>
                        <p><strong>Overdue Since:</strong> {(datetime.now() - task.task_date_time).days if task.task_date_time else 'N/A'} days</p>
                    </div>
                    
                    <p>Please complete this task immediately.</p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending overdue task alert: {str(e)}")
            return False
    
    @staticmethod
    def admin_alert_high_value_deal(opportunity, admin_users):
        """Admin alert for high-value deals"""
        try:
            recipients = [user.email for user in admin_users]
            subject = f"💰 HIGH-VALUE OPPORTUNITY: {opportunity.name.name} - ${opportunity.opportunity_value:,.2f}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #28a745;">💰 High-Value Opportunity</h2>
                    <p>A high-value opportunity has been created or updated.</p>
                    
                    <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                        <p><strong>Opportunity Name:</strong> {opportunity.name.name}</p>
                        <p><strong>Value:</strong> <span style="color: #28a745; font-weight: bold;">${opportunity.opportunity_value:,.2f}</span></p>
                        <p><strong>Related Lead:</strong> {opportunity.lead.name if opportunity.lead else 'N/A'}</p>
                        <p><strong>Stage:</strong> {opportunity.stage.stage if opportunity.stage else 'N/A'}</p>
                        <p><strong>Probability:</strong> {opportunity.probability_in_percentage}%</p>
                        <p><strong>Owner:</strong> {opportunity.owner.first_name if opportunity.owner else 'N/A'} {opportunity.owner.last_name if opportunity.owner else ''}</p>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/opportunities/{opportunity.id}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Opportunity</a></p>
                    
                    <p>Best regards,<br/>CRM System</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending admin alert for high-value deal: {str(e)}")
            return False
    
    @staticmethod
    def re_engagement_email(user):
        """Re-engagement email for inactive users (no login for 30 days)"""
        try:
            recipients = [user.email]
            subject = "👋 We miss you! Let's reconnect."
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>We Miss You, {user.first_name}!</h2>
                    <p>Hi <strong>{user.first_name}</strong>,</p>
                    <p>We noticed you haven't logged into the CRM system for the past 30 days. We'd love to have you back!</p>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p>Your CRM dashboard awaits with important updates:</p>
                        <ul>
                            <li>New leads waiting for follow-up</li>
                            <li>Opportunities in progress</li>
                            <li>Pending tasks and reminders</li>
                        </ul>
                    </div>
                    
                    <p><a href="{settings.FRONTEND_URL}/dashboard" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Log In to CRM</a></p>
                    
                    <p>If you have any questions or need assistance, please reach out to our support team.</p>
                    
                    <p>Best regards,<br/>CRM Support Team</p>
                </body>
            </html>
            """
            
            return EmailNotification.send_email(subject, recipients, html_content)
        except Exception as e:
            logger.error(f"Error sending re-engagement email: {str(e)}")
            return False
