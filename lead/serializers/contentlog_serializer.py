from rest_framework import serializers
from ..models import ContentLog
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ContentLogSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

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
