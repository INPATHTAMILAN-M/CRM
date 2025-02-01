
from rest_framework import serializers
from lead.models import Opportunity_Name

class OpportunityNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = ['id', 'name', 'is_active']

class OpportunityNameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = ['name', 'is_active']

class OpportunityNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = ['name', 'is_active']

class OpportunityNameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = ['id', 'name', 'is_active']

class OpportunityNameRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Name
        fields = ['id', 'name', 'is_active']
