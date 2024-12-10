# serializers.py

from rest_framework import serializers
from ..models import Lead_Status

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = ['id', 'name']  # Specify the fields you want to include in the response

