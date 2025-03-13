from rest_framework import serializers
from django.db import transaction

from lead.models import (
    Contact, Department, Lead_Assignment, Lead_Status, Notification, 
    Opportunity, User, Lead, Opportunity_Stage, 
    Note, Log, Log_Stage, Opportunity_Status, Opportunity_Name
)
from accounts.models import (
    Contact_Status, Lead_Source, 
    Stage, Country, User
)
import datetime
from django.db import transaction
from lead.serializers.lead_serializer import LogSerializer

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = '__all__'
        
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

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
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
        
class LeadSerializer(serializers.ModelSerializer):
    lead_status = LeadStatusSerializer(read_only=True)
    assigned_to = UserSerializer()
    class Meta:
        model = Lead
        fields = ['id', 'name','assigned_to', 'lead_status',"status_date"]  

class ContactSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    created_by =UserSerializer()
    department = DepartmentSerializer(read_only=True)
    lead_source = LeadSourceSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'


class OpportunityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Status
        fields = "__all__"

class OpportunityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = "__all__"


class OpportunityDetailSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    lead = LeadSerializer(read_only=True)
    currency_type= CurrencySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    created_by=OwnerSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    logs = LogSerializer(many=True, read_only=True)
    primary_contact = ContactSerializer(read_only=True)
    opportunity_status = LeadStatusSerializer(read_only=True)
    name = OpportunityNameSerializer(read_only=True)


    class Meta:
        model = Opportunity
        fields = "__all__"

    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000"
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

class OpportunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

    def update(self, instance, validated_data):
        print("Received validated_data:", validated_data)  # Debugging

        old_stage = instance.stage
        new_stage = validated_data.get('stage', old_stage)

        old_opportunity_status = instance.opportunity_status
        new_opportunity_status = validated_data.get('opportunity_status', old_opportunity_status)

        with transaction.atomic():
            # ✅ Update instance fields from validated_data
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # ✅ Save instance after updating fields
            instance.save()

            # ✅ If stage changes, update probability and create Opportunity_Stage
            if old_stage != new_stage:
                instance.probability_in_percentage = new_stage.probability
                instance.save()  # <-- Ensure this is saved immediately
                Opportunity_Stage.objects.create(
                    opportunity=instance,
                    stage=new_stage,
                    moved_by=self.context['request'].user
                )

            # ✅ If opportunity_status changes, log it and update lead status
            if old_opportunity_status != new_opportunity_status:
                instance.status_date = datetime.date.today()
                instance.save()  # <-- Ensure this is saved immediately
                assigned_users = Lead_Assignment.objects.filter(lead=instance.lead).values_list('assigned_to', flat=True).distinct()
                print("assigned_users",assigned_users)

                # Use a transaction to ensure notifications are created atomically
                with transaction.atomic():
                    for user_id in assigned_users:
                        Notification.objects.create(
                            opportunity=instance,
                            receiver_id=user_id,
                            message=f"{self.context['request'].user.first_name} {self.context['request'].user.last_name} changed the status of this Opportunity: '{instance.name.name}'.",
                            assigned_by=self.context['request'].user,
                            type="Opportunity"
                        )

                Log.objects.create(
                    contact=instance.primary_contact,
                    opportunity_status=instance.opportunity_status,
                    opportunity=instance,
                    log_stage=Log_Stage.objects.first(),
                    created_by=self.context['request'].user
                )

                # Update lead status if this is the latest opportunity
                if instance.lead:
                    lead_opportunities = instance.lead.opportunities_leads.order_by('id')
                    first_opportunity = lead_opportunities.first()

                    if first_opportunity == instance:  
                        instance.lead.lead_status = new_opportunity_status
                        instance.lead.save()

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
            'opportunity_status',
            'remark',
            'is_active',
            'opportunity_keyword'
        ]
        read_only_fields = ['created_by']
    
    def create(self, validated_data):
        stage = validated_data.get('stage')
        
        # Start a transaction block for atomic operations
        with transaction.atomic():
            # Create the Opportunity instance
            opportunity = Opportunity.objects.create(**validated_data)
            Log.objects.create(
                contact = opportunity.primary_contact,
                opportunity = opportunity,
                opportunity_status = opportunity.opportunity_status,
                log_stage = Log_Stage.objects.all().first(),
                created_by=self.context['request'].user  # The user creating the opportunity
            )
            assigned_users = Lead_Assignment.objects.filter(lead=opportunity.lead).values_list('assigned_to', flat=True).distinct()
            print("assigned_users",assigned_users)

                # Use a transaction to ensure notifications are created atomically
            with transaction.atomic():
                for user_id in assigned_users:
                    Notification.objects.create(
                        opportunity=opportunity,
                        receiver_id=user_id,
                        message=f"{self.context['request'].user.first_name} {self.context['request'].user.last_name} created a new Opportunity: '{opportunity.name.name}'.",
                        assigned_by=self.context['request'].user,
                        type="Opportunity"
                    )
            # Create the Opportunity_Stage record linked to the new Opportunity
            opportunity_stage = Opportunity_Stage(
                opportunity=opportunity,
                stage=stage,
                moved_by=self.context['request'].user 
            )
            opportunity_stage.save() 

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
