from rest_framework import serializers
from accounts.models import Lead_Source

# Serializer for Lead_Source
class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = ['id', 'source', 'description', 'is_active']
