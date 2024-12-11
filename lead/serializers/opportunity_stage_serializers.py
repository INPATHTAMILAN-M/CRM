from rest_framework import serializers
from lead.models import Opportunity_Stage
from ..models import Opportunity, Log_Stage
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]

    class Meta:
        model = User
        fields = ['id', 'full_name', 'groups']

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model= Opportunity
        fields = ['id', 'name']

class OpportunityStageListSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    moved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Opportunity_Stage
        fields = ['id', 'opportunity', 'stage', 'date', 'moved_by']
        read_only_fields = ['date']

class OpportunityStageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Stage
        fields = ['opportunity', 'stage']

class OpportunityStageRetriveSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)
    stage = StageSerializer(read_only=True)
    moved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Opportunity_Stage
        fields = ['id', 'opportunity', 'stage', 'date', 'moved_by']
        read_only_fields = ['date', 'moved_by']

class OpportunityStageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Stage
        fields = ['stage','opportunity']
