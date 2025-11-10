from rest_framework import serializers
from lead.models import Notification,Task 
from ..models import (
    Lead,Contact,Opportunity, Opportunity_Name, 
    TaskConversationLog
)
from accounts.models import Stage

from ..models import Lead_Status,Opportunity_Name
from django.contrib.auth.models import User

class LeadContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id','name']

class ContactSerializer(serializers.ModelSerializer):
    lead = LeadContactSerializer(read_only=True)
    status = serializers.StringRelatedField()
    
    class Meta:
        model = Contact
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','groups', 'email', 'is_active']

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = '__all__'
        
class LeadSerializer(serializers.ModelSerializer):
    primary_contact = ContactSerializer(read_only=True)
    assigned_to = UserSerializer()
    opportunity_remark = serializers.SerializerMethodField()
    opportunity_status = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ['id', 'name', 'primary_contact', 'assigned_to', 'opportunity_remark', 'opportunity_status']

    def get_lead_owner(self, obj):
        return {
            'id': obj.lead_owner.id,
            'username': obj.lead_owner.username
        }

    def get_opportunity_remark(self, obj):
        opportunity = Opportunity.objects.filter(lead=obj).first()
        return opportunity.remark if opportunity else None

    def get_opportunity_status(self, obj):
        opportunity = Opportunity.objects.filter(lead=obj).first()
        return LeadStatusSerializer(opportunity.opportunity_status).data if opportunity else None

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


class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact','task_type']

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stage
        fields = ['id', 'stage']


class OpportunityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = "__all__"


class OpportunitySerializer(serializers.ModelSerializer):
    lead = LeadSerializer(read_only=True)
    primary_contact = ContactSerializer(read_only=True)
    opportunity_status = LeadStatusSerializer(read_only=True)
    name = OpportunityNameSerializer(read_only=True)
    
    class Meta:
        model = Opportunity
        fields = [
            'id', 'lead', 'primary_contact', 'name',  
             'opportunity_status', 'status_date', 'remark', 
        ]


class TaskConversationLogListSerializer(serializers.ModelSerializer):
    task = TaskListSerializer()
    seen_by = UserSerializer(many=True)
    created_by = UserSerializer()

    class Meta:
        model = TaskConversationLog
        fields = '__all__'

class NotificationRetrieveSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    task = TaskListSerializer()
    opportunity = OpportunitySerializer()
    conversation = TaskConversationLogListSerializer()
    receiver = UserSerializer()
    contact = ContactSerializer()
    
    class Meta:
        model = Notification
        fields = '__all__'
        
class NotificationListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    task = TaskListSerializer()
    opportunity = OpportunitySerializer()
    conversation = TaskConversationLogListSerializer()
    receiver = UserSerializer()
    contact = ContactSerializer()
    assigned_by = UserSerializer()

    class Meta:
        model = Notification
        fields = '__all__'
    

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['lead','task','opportunity','conversation','receiver', 
                  'assigned_by','message', 'type']


