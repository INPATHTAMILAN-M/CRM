from rest_framework import serializers

from lead.serializers.log_serializer import LogStageSerializer
from ..models import Lead,Employee,Contact, Log,Opportunity
from accounts.models import Focus_Segment,Market_Segment,Country, Stage,State,Tag,Vertical,Lead_Source, Lead_Source_From
from ..models import Lead_Status, Department, Contact_Status 
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
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class ContactSerializerList(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()
    
    class Meta:
        model = Contact
        fields = '__all__'
        
class ContactSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()

    class Meta:
        model = Contact
        fields = '__all__'


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name']  

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','currency_short']  

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stage
        fields = ['id', 'stage']


class OpportunitySerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    
    class Meta:
        model = Opportunity
        fields = "__all__"

    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000/"
            return f"{domain}{file_url}"
        return None


# class OpportunitySerializer(serializers.ModelSerializer):
#     # You can add related fields here as needed
#     primary_contact = ContactSerializer(read_only=True)

#     class Meta:
#         model = Opportunity
#         fields = [
#             'id', 'name', 'owner', 'note', 'opportunity_value',
#             'recurring_value_per_year', 'currency_type', 'closing_date', 'stage',
#             'probability_in_percentage', 'file', 'primary_contact', 'created_by'
#         ]
class LogSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
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
    tags = TagSerializer(many=True)
    lead_owner = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    primary_contact = ContactSerializer(read_only=True)
    opportunities = OpportunitySerializer(many=True, read_only=True)
    contacts = ContactSerializerList(many=True, read_only=True)
    assigned_to = serializers.SerializerMethodField()
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
        # Retrieve the latest log for this lead
        latest_log = Log.objects.filter(lead=obj).last()
        # If a log exists, return the follow_up_date_time, otherwise return None
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
        
    def get_assigned_to(self, obj):
        return {
            'id': obj.assigned_to.id,
            'username': obj.assigned_to.username
        }

    def to_representation(self, instance):
        # Get the basic representation first
        representation = super().to_representation(instance)

       
        # if instance.opportunity_set.exists():
        
        representation['opportunities'] = OpportunitySerializer(instance.opportunity_set.all(), many=True).data

        # If no opportunities, include primary contact details only
        primary_contact_data = ContactSerializer(instance.contact_set.filter(is_primary=True).first()).data
        representation['primary_contact'] = primary_contact_data
        representation['logs'] = LogSerializer(instance.log_set.all(), many=True).data 
        representation['contacts'] = ContactSerializer(instance.contact_set.all(), many=True).data
        return representation

class PostContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'status', 'designation', 'department', 'phone_number', 'email_id', 'lead_source', 'is_active', 'is_primary']
        read_only_fields = ['created_by']


class PostLeadSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'focus_segment', 'lead_owner', 'country', 'state', 
            'company_website', 'fax', 'annual_revenue', 'tags', 'market_segment', 
            'is_active', 'lead_type', 'assigned_to', 'lead_source', 'lead_source_from', 'contact_id'
        ]
        read_only_fields = ['created_by']