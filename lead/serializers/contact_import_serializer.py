from rest_framework import serializers
from ..models import Contact, Contact_Status, Department, Lead_Source, Lead_Source_From
from django.core.exceptions import ObjectDoesNotExist


class ContactImportCreateSerializer(serializers.ModelSerializer):
    lead = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=True)  # Assume this is required
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


    def validate_company_name(self, value):
        """Check if the company name already exists."""
        existing_contact = Contact.objects.filter(company_name=value).first()
        if existing_contact:
            raise serializers.ValidationError({
                "message": "Contact with this company name already exists",
                "company_name": value,
                "created_by": existing_contact.created_by
            })
        return value

    def validate_phone_number(self, value):
        """Check if the phone number already exists."""
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
        """Validate the contact status."""
        if value:
            try:
                Contact_Status.objects.get(status=value, is_active=True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Contact status '{value}' not found")
        return value

    def validate_department(self, value):
        """Validate the department."""
        if value:
            try:
                Department.objects.get(department=value, is_active=True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Department '{value}' not found")
        return value

    def validate_lead_source(self, value):
        """Validate the lead source."""
        if value:
            try:
                Lead_Source.objects.get(source=value, is_active=True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Lead source '{value}' not found")
        return value

    def validate_lead_source_from(self, value):
        """Validate the lead source from."""
        if value:
            try:
                Lead_Source_From.objects.get(source_from=value, is_active=True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Lead source from '{value}' not found")
        return value

    def create(self, validated_data):
        """Create the contact entry."""
        return Contact.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update the contact entry (if necessary)."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
