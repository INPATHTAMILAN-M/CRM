from rest_framework import serializers

from lead.serializers.lead_serializer import  LeadSourceSerializer
from ..models import Contact, Lead, Contact_Status, Lead_Source
from django.contrib.auth.models import User
from ..models import Department

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
