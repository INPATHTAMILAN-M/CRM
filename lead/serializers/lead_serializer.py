from rest_framework import serializers
from ..models import Lead,Employee,Contact,Opportunity
from accounts.models import Focus_Segment,Market_Segment,Country,State,Tag,Vertical
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
    id=serializers.IntegerField(source='user.id',read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'username']

class ContactSerializer(serializers.ModelSerializer):
    # You can include any additional fields you need from the Contact model
    class Meta:
        model = Contact
        fields = ['id', 'name', 'designation', 'department', 'phone_number', 'email_id']

class OpportunitySerializer(serializers.ModelSerializer):
    # You can add related fields here as needed
    primary_contact = ContactSerializer(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'owner', 'note', 'opportunity_value',
            'recurring_value_per_year', 'currency_type', 'closing_date', 'stage',
            'probability_in_percentage', 'file', 'primary_contact', 'created_by'
        ]

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
    class Meta:
        model = Lead
        fields = '__all__'

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

        # Check if the lead has associated opportunities
        if instance.opportunity_set.exists():
            # If opportunities exist, include their details
            opportunities_data = OpportunitySerializer(instance.opportunity_set.all(), many=True).data
            representation['opportunities'] = opportunities_data
        else:
            # If no opportunities, include primary contact details only
            primary_contact_data = ContactSerializer(instance.contact_set.filter(is_primary=True).first()).data
            representation['primary_contact'] = primary_contact_data

        return representation

class PostContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'status', 'designation', 'department', 'phone_number', 'email_id', 'lead_source', 'is_active', 'is_primary']
        read_only_fields = ['created_by']


class PostLeadSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    
    class Meta:
        model=Lead
        fields=['id','name','focus_segment','lead_owner','country','state','company_number','company_email','department','lead_status',
                'company_website','fax','annual_revenue','tags','market_segment','is_active','lead_type','assigned_to','lead_source','lead_source_from']
        
        read_only_fields=['created_by']
