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

    def get_display_date(self, obj):
        created = getattr(obj, 'created_on', None)
        updated = getattr(obj, 'updated_on', None)
        if created and updated:
            try:
                return updated if updated > created else created
            except (TypeError, ValueError):
                return created
        return created or updated

    def get_display_date_source(self, obj):
        created = getattr(obj, 'created_on', None)
        updated = getattr(obj, 'updated_on', None)
        if created and updated:
            try:
                return 'updated_on' if updated > created else 'created_on'
            except (TypeError, ValueError):
                return 'created_on'
        return 'created_on' if created else ('updated_on' if updated else None)

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        display_date = self.get_display_date(obj)
        ret['display_date'] = display_date.isoformat() if display_date else None
        ret['display_date_source'] = self.get_display_date_source(obj)
        return ret


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

    def get_display_date(self, obj):
        created = getattr(obj, 'created_on', None)
        updated = getattr(obj, 'updated_on', None)

        if created and updated:
            try:
                if updated > created:
                    return updated
                elif updated == created:
                    return created
                else:
                    return created
            except Exception:
                return created
        elif created:
            return created
        elif updated:
            return updated
        return None

    def get_display_date_source(self, obj):
        created = getattr(obj, 'created_on', None)
        updated = getattr(obj, 'updated_on', None)

        if created and updated:
            try:
                if updated > created:
                    return 'updated_on'
                elif updated == created:
                    return 'created_on'
                else:
                    return 'created_on'
            except Exception:
                return 'created_on'
        elif created:
            return 'created_on'
        elif updated:
            return 'updated_on'
        return None

    def to_representation(self, obj):
        ret = super().to_representation(obj)
        display_date = self.get_display_date(obj)
        ret['display_date'] = display_date.isoformat() if display_date else None
        ret['display_date_source'] = self.get_display_date_source(obj)
        return ret

# class ContactListSerializer(serializers.ModelSerializer):
#     lead = LeadSerializer()
#     status = ContactStatusSerializer()
#     department = DepartmentSerializer(read_only=True)
#     created_by =UserSerializer()
#     lead_source = LeadSourceSerializer(read_only=True)
#     assigned_to = UserSerializer(read_only=True)
    
#     class Meta:
#         model = Contact
#         fields = '__all__'

#     def get_display_date(self, obj):
#         """Return the preferred date according to rules:
#         - If updated_on exists and is strictly greater than created_on -> updated_on
#         - Else -> created_on
#         If both are equal or updated_on missing, created_on is returned.
#         """
#         created = getattr(obj, 'created_on', None)
#         updated = getattr(obj, 'updated_on', None)

#         if updated and created:
#             try:
#                 if updated > created:
#                     return updated
#             except Exception:
#                 # In case of mixed types or timezone issues, fall back to created
#                 return created
#         # If updated missing or not greater, return created (or updated if created missing)
#         return created or updated

#     def get_display_date_source(self, obj):
#         created = getattr(obj, 'created_on', None)
#         updated = getattr(obj, 'updated_on', None)
#         if updated and created:
#             try:
#                 if updated > created:
#                     return 'updated_on'
#             except Exception:
#                 return 'created_on'
#         return 'created_on' if created else ('updated_on' if updated else None)

#     def to_representation(self, obj):
#         """Inject display_date and display_date_source into the serialized output.

#         This avoids needing to enumerate every model field while still returning
#         the additional computed fields requested.
#         """
#         ret = super().to_representation(obj)
#         display_date = self.get_display_date(obj)
#         # DRF will handle datetime conversion for model fields, but since we're
#         # injecting here, convert to ISO string for consistency.
#         ret['display_date'] = display_date.isoformat() if display_date is not None else None
#         ret['display_date_source'] = self.get_display_date_source(obj)
#         return ret

# class ContactDetailSerializer(serializers.ModelSerializer):
#     lead = LeadSerializer()
#     status = ContactStatusSerializer()
#     department = DepartmentSerializer(read_only=True)
#     created_by =UserSerializer()
#     lead_source = LeadSourceSerializer(read_only=True)
#     assigned_to = UserSerializer(read_only=True)
#     class Meta:
#         model = Contact
#         fields = '__all__'

#     # Provide same display logic in the detail serializer so single-object responses
#     # follow the same rule as list responses.
#     def get_display_date(self, obj):
#         created = getattr(obj, 'created_on', None)
#         updated = getattr(obj, 'updated_on', None)
#         if updated and created:
#             try:
#                 if updated > created:
#                     return updated
#             except Exception:
#                 return created
#         return created or updated

#     def get_display_date_source(self, obj):
#         created = getattr(obj, 'created_on', None)
#         updated = getattr(obj, 'updated_on', None)
#         if updated and created:
#             try:
#                 if updated > created:
#                     return 'updated_on'
#             except Exception:
#                 return 'created_on'
#         return 'created_on' if created else ('updated_on' if updated else None)

#     def to_representation(self, obj):
#         ret = super().to_representation(obj)
#         display_date = self.get_display_date(obj)
#         ret['display_date'] = display_date.isoformat() if display_date is not None else None
#         ret['display_date_source'] = self.get_display_date_source(obj)
#         return ret

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
