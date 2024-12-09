from rest_framework import serializers
from .models import Lead_Source, Lead_Source_From

# Serializer for Lead_Source
class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = ['id', 'source', 'description', 'is_active']

# Serializer for Lead_Source_From
class LeadSourceFromSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source_From
        fields = ['id', 'source_from', 'description', 'is_active']

