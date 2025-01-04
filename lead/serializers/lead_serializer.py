from rest_framework import serializers
from django.utils import timezone
from lead.serializers.log_serializer import LogStageSerializer
from ..models import Lead,Employee,Contact, Log,Opportunity
from accounts.models import City, Focus_Segment,Market_Segment,Country, Stage,State,Tag,Vertical,Lead_Source, Lead_Source_From
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
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

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
    city = CitySerializer(read_only=True)
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
    logs = serializers.SerializerMethodField()
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
    
    def get_logs(self, obj):
        """
        Custom method to get all logs related to the contacts of this lead.
        Fetches all logs for each contact linked to this lead.
        """
        contact_logs = Log.objects.filter(contact__lead=obj).select_related('contact').all()
        
        # Serialize the logs related to each contact
        logs_serializer = LogSerializer(contact_logs, many=True)
        return logs_serializer.data
    
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

        # Include opportunities ordered by 'created_on'
        opportunities = instance.opportunity_set.all().order_by('-id')
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
        
        # Include logs related to the lead's contacts
        logs = instance.log_set.all().order_by('-created_on')
        representation['logs'] = LogSerializer(logs, many=True).data
        
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
            'id', 'name', 'focus_segment', 'lead_owner', 'country', 'state', 'city','address',
            'company_website', 'fax', 'annual_revenue', 'tags', 'market_segment', 'lead_status',
            'is_active', 'lead_type', 'assigned_to', 'lead_source', 'lead_source_from', 'department','contact_id','remark','status_date'
        ]
        read_only_fields = ['created_by']
        
    def create(self, validated_data):
        # Extract contact_id from validated_data and remove it
        contact_id = validated_data.pop('contact_id', None)
        # Extract tags from validated_data before creating the lead
        tags_data = validated_data.pop('tags', [])

        # Create the Lead instance
        lead = Lead.objects.create(**validated_data)

        # If contact_id is provided, link the contact to the created lead using the ID (not the Contact object itself)
        if contact_id:
            try:
                contact = Contact.objects.get(id=contact_id.id)
                contact.lead = lead
                contact.is_primary = True  # Optional: set this contact as the primary contact for the lead
                contact.save()
            except Contact.DoesNotExist:
                raise serializers.ValidationError("Contact with the provided ID does not exist.")

        # Assign tags to the lead using .set()
        if tags_data:
            lead.tags.set(tags_data)

        # Return the created lead instance
        return lead
    
    # def update(self, instance, validated_data):
    #     # Check if 'lead_status' has changed
    #     new_lead_status = validated_data.get('lead_status', instance.lead_status)
        
    #     # Perform the actual update of the instance
    #     instance = super().update(instance, validated_data)
        
    #     # If the lead status has changed, update the status_date
    #     if instance.lead_status:
    #         instance.status_date = timezone.now().date()
    #         instance.save()  # Save after updating the status_date
        
    #     return instance