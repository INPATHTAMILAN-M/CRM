from django.db import models
from django.contrib.auth.models import User
from accounts.models import (
    City,
    Focus_Segment,
    Market_Segment,
    Log_Stage,
    Country,
    State,
    Tag,
    Contact_Status,
    Lead_Source,
    Stage,
    Lead_Source_From
)

class Lead_Status(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Lead_Bucket(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

class Department(models.Model):
    department = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.department

class Designation(models.Model):
    designation = models.CharField(max_length=255)
   

    def __str__(self):
        return self.designation

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country_code = models.ForeignKey(Country, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    joined_on = models.DateField()
    profile_photo = models.ImageField(upload_to='employee_photos', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')])
    blood_group = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')])
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f' {self.user.username} - {self.designation}'

class Lead(models.Model):
    name = models.CharField(max_length=255,unique=True)
    focus_segment = models.ForeignKey(Focus_Segment, on_delete=models.CASCADE)
    lead_owner = models.ForeignKey(User, related_name='leads_owned', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='leads_created', on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)
    company_website = models.CharField(max_length=255, null=True, blank=True)
    fax = models.CharField(max_length=255, null=True, blank=True)
    annual_revenue = models.FloatField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    market_segment = models.ForeignKey(Market_Segment, on_delete=models.CASCADE)
    lead_source = models.ForeignKey(Lead_Source, on_delete=models.CASCADE, null=True, blank=True)
    lead_source_from = models.ForeignKey(Lead_Source_From, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    lead_status = models.ForeignKey(Lead_Status, on_delete=models.CASCADE, null=True, blank=True)
    status_date = models.DateField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    
    LEAD_TYPE_CHOICES = [
        ('Digital Lead', 'Digital Lead'),
        ('Manual Lead', 'Manual Lead'),
    ]
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} owner {self.lead_owner.username}'

class Contact(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True,related_name="contact_leads")
    company_name = models.CharField(max_length=255, null=True, blank=True,unique=True)
    name = models.CharField(max_length=255)
    status = models.ForeignKey(Contact_Status, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    email_id = models.EmailField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    lead_source = models.ForeignKey(Lead_Source, on_delete=models.CASCADE, null=True, blank=True)
    lead_source_from = models.ForeignKey(Lead_Source_From, on_delete=models.CASCADE, null=True, blank=True)
    source_from = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Lead_Assignment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='assigned_leads', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='assigned_by_leads', on_delete=models.CASCADE)
    assigned_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.lead.name} assigned to {self.assigned_to.username}'

class Opportunity(models.Model):
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL)
    primary_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE,null=True, blank=True)
    owner = models.ForeignKey(User, related_name='opportunities_owned', on_delete=models.CASCADE,null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    opportunity_value = models.FloatField()
    recurring_value_per_year = models.FloatField(null=True, blank=True)
    currency_type = models.ForeignKey(Country, on_delete=models.CASCADE,null=True, blank=True)
    closing_date = models.DateField()
    probability_in_percentage = models.FloatField()
    lead_bucket = models.ForeignKey(Lead_Bucket, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to='opportunity_files', null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='created_opportunities', on_delete=models.CASCADE)
    remark = models.TextField(null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Opportunity_Stage(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Stage: {self.stage.stage} for {self.opportunity.name}'

class Log(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,related_name="contact_logs")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE,null=True, blank=True)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True)
    focus_segment = models.ForeignKey(Focus_Segment, null=True, blank=True, on_delete=models.CASCADE)
    follow_up_date_time = models.DateTimeField(null=True, blank=True)
    log_stage = models.ForeignKey(Log_Stage, on_delete=models.CASCADE)
    details = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='logs_files', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    lead_log_status = models.ForeignKey(Lead_Status, on_delete=models.CASCADE, null=True, blank=True)
    
    LOG_TYPE_CHOICES = [
    ('Call', 'Call'),
    ('Meeting', 'Meeting'),
    ('Email', 'Email'),
    ]
    log_type= models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, null=True, blank=True)


    def __str__(self):
        return f'Log for {self.contact.name}'

class Task(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    log = models.ForeignKey(Log, on_delete=models.CASCADE, null=True, blank=True)
    task_date_time = models.DateTimeField(null=True, blank=True)
    task_detail = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    task_creation_type = models.CharField(max_length=10, choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')])
    remark = models.TextField(null=True, blank=True)
    
    TASK_TYPE_CHOICES = [
    ('Call', 'Call'),
    ('Follow Up', 'Follow Up'),
    ('To Do', 'To Do'),
    ]
    task_type= models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f'Task for {self.contact.name}'

class Task_Assignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_task_assignments')
    assigned_to = models.ForeignKey(User, related_name='task_assignments', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)
    assigned_on = models.DateField(auto_now_add=True)
    assignment_note = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Task assigned to {self.assigned_to.username}'

class Note(models.Model):
    opportunity = models.ForeignKey(Opportunity, related_name='notes', on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)
    note_by = models.ForeignKey(User, on_delete=models.CASCADE)
    note_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Note for {self.opportunity.name}'

class Email_Communication(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_emails', on_delete=models.CASCADE)
    to_users = models.ManyToManyField(User, related_name='received_emails')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return f'Email from {self.from_user.username} to {self.to_users.count()} users'
    
class Notification(models.Model):
    receiver=models.ForeignKey(User, related_name='notification_receiver', on_delete=models.CASCADE)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)