
from rest_framework import serializers
from ..models import City, Country, State

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    class Meta:
        model = State
        fields = '__all__'


class GetCitySerializer(serializers.ModelSerializer):
    state = StateSerializer()
    class Meta:
        model = City
        fields = ['id', 'state', 'city_name']

class CreateCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'state', 'city_name']
 
 