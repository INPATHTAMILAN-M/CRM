from rest_framework import serializers

from accounts.models import Country
from ..models import State

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

# Serializer for State
class StateSerializer(serializers.ModelSerializer):
    Country = CountrySerializer()
    class Meta:
        model = State
        fields = '__all__'
