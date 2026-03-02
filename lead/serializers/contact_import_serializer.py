from rest_framework import serializers
from ..models import Contact, Contact_Status, Department, Lead_Source, Lead_Source_From, ContentLog, Lead
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd

class ContactImportCreateSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), required=False, allow_null=True
    )
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    designation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    secondary_phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email_id = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    remark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lead_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lead_source_from = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)
    is_archive = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Contact
        fields = '__all__'

    # --- VALIDATIONS ---

    def validate_company_name(self, value):
        existing_contact = Contact.objects.filter(company_name=value).first()
        if existing_contact:
            raise serializers.ValidationError({
                "message": "Contact with this company name already exists",
                "company_name": value,
                "created_by": existing_contact.created_by
            })
        return value

    def validate_phone_number(self, value):
        if not value:
            return value
        existing_contact = Contact.objects.filter(phone_number=value).first()
        if existing_contact:
            raise serializers.ValidationError({
                "message": "Contact with this phone number already exists",
                "phone_number": value,
                "company_name": existing_contact.company_name,
                "created_by": existing_contact.created_by
            })
        return value

    def validate_status(self, value):
        if not value:
            return None
        try:
            return Contact_Status.objects.get(status=value, is_active=True)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Contact status '{value}' not found")

    def validate_department(self, value):
        if not value:
            return None
        try:
            return Department.objects.get(department=value, is_active=True)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Department '{value}' not found")

    def validate_lead_source(self, value):
        if not value:
            return None
        try:
            return Lead_Source.objects.get(source=value, is_active=True)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Lead source '{value}' not found")

    def validate_lead_source_from(self, value):
        if not value:
            return None
        try:
            return Lead_Source_From.objects.get(source_from=value, is_active=True)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Lead source from '{value}' not found")

    # --- CREATE / UPDATE ---

    def create(self, validated_data):
        """Create the contact entry and log."""
        contact = Contact.objects.create(**validated_data)
        
        # Create ContentLog entry
        ContentLog.objects.create(
            contact=contact,
            created_by=contact.created_by,
            description=f"Contact created via Import for {contact.company_name}",
            proposal='Contact',
            lead=contact.lead,
            company_name=contact.company_name,
            contact_name=contact.name,
            phone_number=contact.phone_number,
            secondary_phone_number=contact.secondary_phone_number,
            email_id=contact.email_id,
            designation=contact.designation,
            department=contact.department,
            remark=contact.remark,
            status=contact.status,
            lead_source=contact.lead_source,
            lead_source_from=contact.lead_source_from,
            source_from=contact.source_from,
            assigned_to=contact.assigned_to,
            is_primary=contact.is_primary,
            is_archive=contact.is_archive
        )
        return contact

    def update(self, instance, validated_data):
        """Update the contact entry."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


from rest_framework import serializers

class BulkImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        """Ensure it's a valid Excel file"""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("Only Excel files (.xlsx, .xls) are allowed.")
        return value