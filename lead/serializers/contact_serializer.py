from rest_framework import serializers
from ..models import Contact, Lead, Contact_Status, Lead_Source
from django.contrib.auth.models import User

from rest_framework import serializers
from ..models import Contact

#contactserializer.py

from rest_framework import serializers
from ..models import Contact, Lead, Contact_Status, Lead_Source
from django.contrib.auth.models import User

class ContactSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(queryset=Lead.objects.all())
    status = serializers.PrimaryKeyRelatedField(queryset=Contact_Status.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Contact
        fields = '__all__'

    # Overriding to_representation to customize output format
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        representation['lead'] = {
            'id': instance.lead.id,
            'name': instance.lead.name,
        } if instance.lead else None

        representation['status'] = {
            'id': instance.status.id,
            'status': instance.status.status,
        } if instance.status else None

        representation['created_by'] = {
            'id': instance.created_by.id,
            'username': instance.created_by.username,
        } if instance.created_by else None
        
        return representation


class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = ['id','status']



class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = ['id','source']



class PostContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields='__all__'
        read_only_fields=['created_by']