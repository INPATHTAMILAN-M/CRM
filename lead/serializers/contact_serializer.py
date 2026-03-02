from rest_framework import serializers

from lead.serializers.lead_serializer import  LeadSourceSerializer
from ..models import Contact, Lead, Contact_Status, Lead_Source, ContentLog
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
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'groups']

class ContactListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    department = DepartmentSerializer(read_only=True)
    created_by = UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'


class ContactDetailSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    status = ContactStatusSerializer()
    department = DepartmentSerializer(read_only=True)
    created_by = UserSerializer()
    lead_source = LeadSourceSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ('created_by',)

        extra_kwargs = {
                'company_name': {'validators': []},
                'phone_number': {'validators': []},
            }
    def validate_company_name(self, value):
        existing = Contact.objects.filter(company_name=value).first()
        if existing:
            creator = existing.created_by.username if existing.created_by else "Unknown"

            raise serializers.ValidationError(
                f"Company name already exists. Created by: {creator}"
            )
        return value

    def validate_phone_number(self, value):
        existing = Contact.objects.filter(phone_number=value).first()
        if existing:
            creator = existing.created_by.username if existing.created_by else "Unknown"

            raise serializers.ValidationError(
                f"Phone number already exists. Created by: {creator}"
            )
        return value

    def create(self, validated_data):
        # Set created_by to the current user
        validated_data['created_by'] = self.context['request'].user
        
        # Create the Contact
        contact = Contact.objects.create(**validated_data)
        
        # Create ContentLog entry for the contact with all contact fields
        ContentLog.objects.create(
            contact=contact,
            created_by=self.context['request'].user,
            description=f"Contact created for {contact.company_name}",
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
        

class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ('created_by',)

    def update(self, instance, validated_data):
        instance.updated_on = timezone.now()
        ignore_fields = {'created_on', 'updated_on', 'created_by'}

        def get_comparable_value(value):
            if value is None:
                return None
            if hasattr(value, 'pk'):
                return value.pk
            return value

        changed_fields = []
        for field_name, new_value in validated_data.items():
            if field_name in ignore_fields:
                continue

            current_value = getattr(instance, field_name)
            if get_comparable_value(current_value) != get_comparable_value(new_value):
                changed_fields.append(field_name)
        
        if assigned_to := validated_data.get('assigned_to'):
            instance.assigned_to = assigned_to
            Notification.objects.create(
                message=f'Contact {instance.name} has been assigned to you.',
                receiver=assigned_to,
                contact=instance,
                assigned_by=self.context['request'].user,
                type = 'Contact'
            )

        updated_contact = super().update(instance, validated_data)

        if changed_fields:
            field_mapping = {
                'lead': 'lead',
                'company_name': 'company_name',
                'name': 'contact_name',
                'phone_number': 'phone_number',
                'secondary_phone_number': 'secondary_phone_number',
                'email_id': 'email_id',
                'designation': 'designation',
                'department': 'department',
                'remark': 'remark',
                'status': 'status',
                'lead_source': 'lead_source',
                'lead_source_from': 'lead_source_from',
                'source_from': 'source_from',
                'assigned_to': 'assigned_to',
                'is_primary': 'is_primary',
                'is_archive': 'is_archive',
            }

            log_data = {
                'contact': updated_contact,
                'created_by': self.context['request'].user,
                'description': f"Contact updated fields: {', '.join(changed_fields)}",
                'proposal': 'Contact',
            }

            for contact_field in changed_fields:
                content_log_field = field_mapping.get(contact_field)
                if content_log_field:
                    log_data[content_log_field] = getattr(updated_contact, contact_field)

            ContentLog.objects.create(**log_data)
        
        return updated_contact
