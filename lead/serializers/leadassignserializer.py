from rest_framework import serializers
from ..models import Lead_Assignment

class LeadAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Assignment
        fields = '__all__'
