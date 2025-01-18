from rest_framework import serializers

from accounts.models import Country
from ..models import State

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

# Serializer for State
class GetStateSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    class Meta:
        model = State
        fields = '__all__'

class CreateStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'
