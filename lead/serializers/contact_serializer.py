from rest_framework import serializers

from lead.serializers.lead_serializer import  LeadSourceSerializer
from ..models import Contact, Lead, Contact_Status, Lead_Source
from django.contrib.auth.models import User
from ..models import Department
from django.utils import timezone
from ..models import Notification

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department'] 
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class ContactListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    department = DepartmentSerializer(read_only=True)
    created_by =UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'

class ContactDetailSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    department = DepartmentSerializer(read_only=True)
    created_by =UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'

class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ('created_by',)
        

class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ('created_by',)

    def update(self, instance, validated_data):
        instance.updated_on = timezone.now()
        if assigned_to := validated_data.get('assigned_to'):
            instance.assigned_to = assigned_to
            Notification.objects.create(
                message=f'Contact {instance.name} has been assigned to you.',
                receiver=assigned_to,
                contact=instance,
                assigned_by=self.context['request'].user,
                type = 'Contact'
            )

        return super().update(instance, validated_data)
