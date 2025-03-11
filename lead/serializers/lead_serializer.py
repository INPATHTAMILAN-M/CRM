from rest_framework import serializers
from django.utils import timezone
from lead.serializers.log_serializer import LogStageSerializer
from ..models import Lead,Employee,Contact, Lead_Assignment, Log, Notification,Opportunity, Opportunity_Status, Opportunity_Name, Task_Assignment
from accounts.models import (
    City, Focus_Segment,Market_Segment,
    Country, Stage,State,Tag,Vertical,
    Lead_Source, Lead_Source_From
)
from django.db import transaction
from ..models import Lead_Status, Department, Contact_Status, Log_Stage, Opportunity_Name
from django.contrib.auth.models import User

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
    market_segment = MarketSegmentSerializer(read_only=True)
    focus_segment = FocusSegmentSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    tags = TagSerializer(many=True)
    lead_owner = UserSerializer()
    created_by = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    opportunities = OpportunitySerializer(many=True, read_only=True)
    contacts = ContactSerializerList(many=True, read_only=True)
    assigned_to = UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)  # Nested serializer for LeadSource
    lead_source_from = LeadSourceFromSerializer(read_only=True)  # Nested serializer for LeadSourceFrom
    lead_status = LeadStatusSerializer(read_only=True)  # Nested serializer for LeadStatus
    department = DepartmentSerializer(read_only=True)  # Nested serializer for Department
    last_log_follow_up = serializers.SerializerMethodField()
    logs = LogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'

    def get_last_log_follow_up(self, obj):
        """
        Custom method to get the last follow-up date from the logs
        for this lead's contacts.
        """
        latest_log = Log.objects.filter(contact__lead=obj).order_by('-follow_up_date_time').first()
        if latest_log:
            return latest_log.follow_up_date_time
        return None
    
    def get_lead_owner(self, obj):
        return {
            'id': obj.lead_owner.id,
            'username': obj.lead_owner.username
        }

    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'username': obj.created_by.username
        }
        
    def to_representation(self, instance):
        # Get the basic representation first
        representation = super().to_representation(instance)

        # Include opportunities ordered by 'created_on'
        opportunities = instance.opportunities_leads.all().order_by('-id')
        representation['opportunities'] = OpportunitySerializer(opportunities, many=True).data

        # Include contacts ordered by 'created_on'
        contacts = instance.contact_leads.all().order_by('-id')  # Use 'contact_leads' instead of 'contact_set'
        representation['contacts'] = ContactSerializerList(contacts, many=True).data
        
        # Primary contact details (only one contact is marked as primary)
        primary_contact = instance.contact_leads.filter(is_primary=True).first()  # Use 'contact_leads'
        if primary_contact:
            primary_contact_data = ContactSerializer(primary_contact).data
            representation['primary_contact'] = primary_contact_data
        else:
            representation['primary_contact'] = None
        # Include logs for the lead
        logs = instance.log_set.all().order_by('-created_on')  # Assuming 'log_set' is the related name for the logs
        representation['logs'] = LogSerializer(logs, many=True).data
        
        return representation

class PostContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'status', 'designation', 'department', 'phone_number', 
                  'email_id', 'lead_source', 'source_form','is_active', 'is_primary']
        read_only_fields = ['created_by']


class PostLeadSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(),required=False)
    opportunity_name = serializers.PrimaryKeyRelatedField(queryset=Opportunity_Name.objects.all(),required=False)
    opportunity_keyword = serializers.CharField(required=False, allow_blank=True)  # Add this line for the text field

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'focus_segment', 'lead_owner', 'country', 'state', 'city', 'address',
            'company_website', 'fax', 'annual_revenue', 'tags', 'market_segment', 'lead_status',
            'is_active', 'lead_type', 'assigned_to', 'lead_source', 'lead_source_from', 'department',
            'contact_id', 'remark', 'status_date', 'opportunity_name','opportunity_keyword'
        ]
        read_only_fields = ['created_by']
        
    @transaction.atomic
    def create(self, validated_data):
        contact_id = validated_data.pop('contact_id', None)  # This is an ID (integer)
        tags_data = validated_data.pop('tags', [])
        opportunity_name = validated_data.pop('opportunity_name', None)  # Also an ID
        opportunity_keyword = validated_data.pop('opportunity_keyword', None)  # Also an ID


        lead = Lead.objects.create(**validated_data)
        lead.lead_status = Lead_Status.objects.all().order_by('id').first()
        lead.save()
        # Log creation
        Log.objects.create(
            lead=lead,
            created_by=self.context['request'].user,
            contact_id=contact_id.id,  
            details=lead.remark,
            log_type="Call",
            log_stage=Log_Stage.objects.first(),
            focus_segment=lead.focus_segment
        )

        if contact_id:
            Contact.objects.filter(id=contact_id.id).update(
                lead=lead,
                is_primary=True
            )
            lead.lead_source = Contact.objects.get(id=contact_id.id).lead_source  # Fetch actual contact
            lead.lead_status = Lead_Status.objects.all().order_by('id').first()
            lead.save()

        # Create Opportunity if opportunity_name_id exists
        print("opportunity_name: " , opportunity_name)
        if opportunity_name:
            opp = Opportunity.objects.create(
                lead=lead,
                created_by=self.context['request'].user,
                name=opportunity_name, 
                stage=Stage.objects.first(),
                opportunity_value=0,
                probability_in_percentage=0,
                remark = lead.remark ,
                primary_contact = contact_id ,
                opportunity_status = Lead_Status.objects.all().order_by('id').first(),
                closing_date=timezone.now().date(),
                opportunity_keyword = opportunity_keyword
            )
            # Fetch all assigned_to users from Lead_Assignment for this lead
            assigned_users = Lead_Assignment.objects.filter(lead=lead).values_list('assigned_to', flat=True)
            for user_id in assigned_users:
                Notification.objects.create(
                    opportunity=opp,
                    receiver_id=user_id,
                    message=f"{self.context['request'].user.first_name} {self.context['request'].user.last_name} created a new Opportunity: '{opportunity_name}'.",
                    type = "Opportunity"
                )
            print(opp)


        if tags_data:
            lead.tags.set(tags_data)

        return lead
    def update(self, instance, validated_data):
        assigned_to = validated_data.get('assigned_to', None)
        
        if assigned_to and assigned_to != instance.assigned_to:
            Lead_Assignment.objects.create(
                lead=instance, 
                assigned_to=assigned_to,
                assigned_by=instance.created_by,
            )
        if assigned_to is None:
            Lead_Assignment.objects.create(
                lead=instance,  
                assigned_to=assigned_to,
                assigned_by=instance.created_by,
            )
        print("assigned_to",assigned_to)
        Notification.objects.create(
                lead=instance,
                receiver=assigned_to,
                message=f"{instance.created_by.first_name} {instance.created_by.last_name} assigned to a new lead: '{instance.name}'.",
                type="Lead"
                )
        return super().update(instance, validated_data)