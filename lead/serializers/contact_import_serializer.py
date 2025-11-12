from rest_framework import serializers
from ..models import Contact, Contact_Status, Department, Lead_Source, Lead_Source_From
from django.core.exceptions import ObjectDoesNotExist

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
        """Create the contact entry."""
        return Contact.objects.create(**validated_data)

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