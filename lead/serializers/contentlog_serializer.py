from rest_framework import serializers
from ..models import ContentLog, Lead, Department, Contact_Status, Lead_Source, Lead_Source_From, Contact
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class LeadDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class DepartmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ContactStatusDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = '__all__'


class LeadSourceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = '__all__'


class LeadSourceFromDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source_From
        fields = '__all__'


class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ContentLogSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    contact = ContactDetailSerializer(read_only=True)
    lead = LeadDetailSerializer(read_only=True)
    department = DepartmentDetailSerializer(read_only=True)
    status = ContactStatusDetailSerializer(read_only=True)
    lead_source = LeadSourceDetailSerializer(read_only=True)
    lead_source_from = LeadSourceFromDetailSerializer(read_only=True)

    class Meta:
        model = ContentLog
        fields = ['id', 'contact', 'created_by', 'created_date', 'updated_date', 'description', 'proposal',
                  'lead', 'company_name', 'contact_name', 'phone_number', 'secondary_phone_number', 'email_id', 
                  'designation', 'department', 'remark', 'status', 'lead_source', 'lead_source_from', 
                  'source_from', 'assigned_to', 'is_primary', 'is_archive']
        read_only_fields = ['created_by', 'created_date', 'updated_date']


class ContentLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLog
        fields = ['contact', 'description', 'proposal']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
