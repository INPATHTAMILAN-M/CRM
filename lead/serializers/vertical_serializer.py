from rest_framework import serializers
from accounts.models import Vertical

class VerticalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = '__all__'  # Or specify a list of fields like ['id', 'vertical', 'description', 'is_active']
