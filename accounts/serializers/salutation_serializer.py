from rest_framework import serializers
from ..models import Salutation

class SalutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ['id', 'salutation', 'is_active']
