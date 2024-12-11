from rest_framework import serializers
from ..models import Market_Segment

# Serializer for Market_Segment
class MarketSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market_Segment
        fields = '__all__'

