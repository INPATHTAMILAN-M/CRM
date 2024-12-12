from rest_framework import serializers
from ..models import Contact_Status

class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = '__all__'
