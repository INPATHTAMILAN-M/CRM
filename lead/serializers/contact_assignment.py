from rest_framework import serializers
from ..models import Contact_Assignment

# Serializer for creating a Contact_Assignment
class ContactAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Assignment
        fields = ['contact', 'assigned_to', 'assigned_by', 'is_active']

# Serializer for updating a Contact_Assignment
class ContactAssignmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Assignment
        fields = ['is_active']

# Serializer for retrieving a Contact_Assignment
class ContactAssignmentRetrieveSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = Contact_Assignment
        fields = ['id', 'contact_name', 'assigned_to_username', 'assigned_by_username', 
                  'assigned_on', 'is_active']
        
class ContactAssignmentListSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = Contact_Assignment
        fields = ['id', 'contact_name', 'assigned_to_username', 'assigned_by_username', 
                  'assigned_on', 'is_active']
