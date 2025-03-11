from rest_framework import serializers
from lead.models import Notification,Task 

from lead.serializers.log_serializer import LogStageSerializer
from ..models import Lead,Employee,Contact, Log,Opportunity, Opportunity_Status, Opportunity_Name, Task_Assignment, TaskConversationLog
from accounts.models import (
    City, Focus_Segment,Market_Segment,
    Country, Stage,State,Tag,Vertical,
    Lead_Source, Lead_Source_From
)
from ..models import Lead_Status, Department, Contact_Status, Opportunity_Name
from django.contrib.auth.models import User

class LeadContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id','name']

class ContactSerializer(serializers.ModelSerializer):
    lead = LeadContactSerializer()
    class Meta:
        model = Contact
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','groups', 'email', 'is_active']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task_Assignment
        fields = ['assigned_to',"assignment_note"]

class TaskAssignmentListSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer()
    assigned_by = UserSerializer()

    class Meta:
        model = Task_Assignment
        fields = ['assigned_to', 'assigned_by', 'assigned_on', 
                  'assignment_note', 'is_active']

class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    # log = LogSerializer()
    # created_by = UserSerializer()
    
    assignment_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'task_date_time', 'task_detail', 
                  'task_type',
                  'assignment_details']

    def get_assignment_details(self, obj):
        task_assignments = obj.task_task_assignments.all()
        return TaskAssignmentListSerializer(task_assignments, many=True).data
     
    


class VerticalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = ['id', 'vertical'] 


class FocusSegmentSerializer(serializers.ModelSerializer):
    vertical = VerticalSerializer(read_only=True)
    class Meta:
        model = Focus_Segment
        fields = ['id','focus_segment','vertical']
    
class MarketSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market_Segment
        fields = ['id','market_segment']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','country_name']
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id','state_name']
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'state', 'city_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','tag']

class EmpSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id',read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'username']
        
class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = '__all__'

class LeadSourceFromSerializer(serializers.ModelSerializer):
    source = LeadSourceSerializer(read_only=True)  # Nested serializer for LeadSource

    class Meta:
        model = Lead_Source_From
        fields = '__all__'

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = '__all__'
 
class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active','groups']

class ContactSerializerList(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()
    department = DepartmentSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'
        
class ContactSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()
    department = DepartmentSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','currency_short']  

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stage
        fields = ['id', 'stage']

class OpportunityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Status
        fields = "__all__"

class OpportunityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = "__all__"


class OpportunitySerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    opportunity_status = OpportunityStatusSerializer(read_only=True)
    name = OpportunityNameSerializer(read_only=True)
    
    class Meta:
        model = Opportunity
        fields = "__all__"

    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000/"
            return f"{domain}{file_url}"
        return None


class LeadLogSerializer(serializers.ModelSerializer):
    market_segment = MarketSegmentSerializer(read_only=True)
    focus_segment = FocusSegmentSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    tags = TagSerializer(many=True)
    lead_owner = UserSerializer()
    created_by = UserSerializer()
    primary_contact = ContactSerializer(read_only=True)
    assigned_to = UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)  # Nested serializer for LeadSource
    lead_source_from = LeadSourceFromSerializer(read_only=True)  # Nested serializer for LeadSourceFrom
    lead_status = LeadStatusSerializer(read_only=True)  # Nested serializer for LeadStatus
    department = DepartmentSerializer(read_only=True)  # Nested serializer for Department

    class Meta:
        model = Lead
        fields = '__all__'
    
    
class LogSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    lead = LeadLogSerializer()
    opportunity = OpportunitySerializer(read_only=True)
    focus_segment = FocusSegmentSerializer(read_only=True)
    log_stage = LogStageSerializer(read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = '__all__'

    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'username': obj.created_by.username
        }

class LeadSerializer(serializers.ModelSerializer):
   
    lead_owner = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    assigned_to = UserSerializer()
    lead_status = LeadStatusSerializer(read_only=True)  # Nested serializer for LeadStatus

    class Meta:
        model = Lead
        fields = ['id', 'name', 'lead_owner', 'created_on', 'lead_status','status_date','primary_contact','assigned_to']

    def get_lead_owner(self, obj):
        return {
            'id': obj.lead_owner.id,
            'username': obj.lead_owner.username
        }

    def to_representation(self, instance):
        # Get the basic representation first
        representation = super().to_representation(instance)

        primary_contact = instance.contact_leads.filter(is_primary=True).first()  # Use 'contact_leads'
        if primary_contact:
            primary_contact_data = ContactSerializer(primary_contact).data
            representation['primary_contact'] = primary_contact_data
        else:
            representation['primary_contact'] = None
       
        return representation

class OpportunityListSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    created_by =UserSerializer()
    opportunity_status = LeadStatusSerializer(read_only=True)
    name = OpportunityNameSerializer(read_only=True)
    
    
    class Meta:
        model = Opportunity
        fields = "__all__"

    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000/"
            return f"{domain}{file_url}"
        return None
class TaskConversationLogListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = TaskConversationLog
        fields = ['id', 'task', 'message', 'created_by', 'created_on', 'seen_by', 'is_viewed']

class NotificationRetrieveSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    task = TaskListSerializer()
    opportunity = OpportunityListSerializer()
    conversation = TaskConversationLogListSerializer()
    receiver = UserSerializer()
    
    class Meta:
        model = Notification
        fields = '__all__'
        
class NotificationListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    task = TaskListSerializer()
    opportunity = OpportunityListSerializer()
    conversation = TaskConversationLogListSerializer()
    receiver = UserSerializer()
    assigned_by = UserSerializer()
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['lead','task','opportunity','conversation','receiver', 'assigned_by','message', 'type']


