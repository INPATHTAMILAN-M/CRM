from rest_framework import serializers
from accounts.models import Lead_Source_From

# Serializer for Lead_Source_From
class LeadSourceFromSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source_From
        fields = ['id', 'source_from', 'description', 'is_active']

