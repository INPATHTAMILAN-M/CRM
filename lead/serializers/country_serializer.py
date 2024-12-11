from rest_framework import serializers
from ..models import Country


# Serializer for Country
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
