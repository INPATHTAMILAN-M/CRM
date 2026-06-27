from rest_framework import serializers
from lead.models import Whatsapp

class WhatsappSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whatsapp
        fields = '__all__'
        read_only_fields = ['created_by']
