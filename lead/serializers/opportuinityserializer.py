from rest_framework import serializers
from lead.models import Contact, Department, Lead_Status, Opportunity, User, Lead, Opportunity_Stage, Note
from accounts.models import Contact_Status, Lead_Source, Stage, Country, User
from django.db import transaction

from lead.serializers.lead_serializer import LogSerializer

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name','assigned_to', 'lead_status']  

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','currency_short']  

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Stage
        fields = ['id', 'stage']
       
class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = '__all__'

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class ContactSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()
    department = DepartmentSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'


class OpportunityDetailSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    logs = LogSerializer(many=True, read_only=True)
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
    
    def to_representation(self, instance):
        # Get the basic representation first
        representation = super().to_representation(instance)
        representation['logs'] = LogSerializer(instance.log_set.all(), many=True).data 
        return representation
    
class OpportunityListSerializer(serializers.ModelSerializer):
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

class OpportunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

    def update(self, instance, validated_data):
        # Get the current stage and the new stage from the incoming data
        old_stage = instance.stage
        new_stage = validated_data.get('stage', old_stage)

        # Start a transaction block for atomic operations
        with transaction.atomic():
            # Update the Opportunity instance
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            # If the stage has changed, update the stage and create an Opportunity_Stage record
            if old_stage != new_stage:
                instance.stage = new_stage
                instance.probability_in_percentage = new_stage.probability  # Assuming you want to update this field
                instance.save()  # Save the Opportunity instance with the new stage

                # Create the Opportunity_Stage record manually
                opportunity_stage = Opportunity_Stage(
                    opportunity=instance,
                    stage=new_stage,
                    moved_by=self.context['request'].user  # Get the user making the change
                )
                opportunity_stage.save()  # Save the new Opportunity_Stage record

            return instance
        
class OpportunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = [
            'id',
            'lead',
            'primary_contact',
            'name',
            'owner',
            'opportunity_value',
            'currency_type',
            'closing_date',
            'probability_in_percentage',
            'stage',
            'note',
            'recurring_value_per_year',
            'file',
            "lead_bucket",
            'file',
            'remark',
            'is_active'
        ]
        read_only_fields = ['created_by']
    
    def create(self, validated_data):
        # Assuming 'stage' is part of the validated data and needs to be used to create the Opportunity_Stage
        stage = validated_data.get('stage')
        
        # Start a transaction block for atomic operations
        with transaction.atomic():
            # Create the Opportunity instance
            opportunity = Opportunity.objects.create(**validated_data)

            # Create the Opportunity_Stage record linked to the new Opportunity
            opportunity_stage = Opportunity_Stage(
                opportunity=opportunity,
                stage=stage,
                moved_by=self.context['request'].user  # The user creating the opportunity
            )
            opportunity_stage.save()  # Save the new Opportunity_Stage record

            return opportunity
        
class LeadNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'name'] 

class StageNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage']

class StageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Stage
        fields='__all__'


class PostNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields='__all__'

class StageGetSerializer(serializers.ModelSerializer):
    opportunity = OpportunityDetailSerializer(read_only=True)
    stage = StageNameSerializer(read_only=True)
    moved_by=OwnerSerializer(read_only=True)
    class Meta:
        model = Opportunity_Stage
        fields='__all__'
