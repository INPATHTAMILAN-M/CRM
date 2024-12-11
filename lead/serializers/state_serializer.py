from rest_framework import serializers
from ..models import State

# Serializer for State
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
