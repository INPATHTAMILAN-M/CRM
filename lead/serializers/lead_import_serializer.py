from rest_framework import serializers
from accounts.models import User
from datetime import datetime
from lead.models import (
    Lead, Opportunity_Status, Contact_Status, Contact, 
    Country, State, City, Opportunity_Name, Lead_Status, Lead_Source
)

class CustomDateField(serializers.DateTimeField):
    def to_internal_value(self, data):
        # Check if the input is an empty string
        if data == "":
            return None  # Convert empty string to None
        # Otherwise, proceed with the default behavior
        return super().to_internal_value(data)

class LeadImportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=50)
    phone_number = serializers.RegexField(regex=r'^\d{10}$', required=False, allow_blank=True, error_messages={
        'invalid': 'Phone number must be a 10-digit number without spaces.'
    })    
    remark = serializers.CharField(max_length=500, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    opportunity_name = serializers.CharField(max_length=200)
    # lead_owner = serializers.CharField(max_length=100,required=False,allow_blank=True)
    opportunity_status = serializers.CharField(max_length=50)
    status_date = CustomDateField()  # ✅ Allows None
    lead_source = serializers.CharField(max_length=50, required=False, allow_blank=True)


    def validate_status(self, value):
        status_obj = Contact_Status.objects.filter(status=value).first()
        if not status_obj:
            raise serializers.ValidationError("Invalid status.")
        return status_obj

    def validate_country(self, value):
        if value:  # ✅ Skip validation if empty
            country_obj = Country.objects.filter(country_name=value).first()
            if not country_obj:
                raise serializers.ValidationError("Invalid country.")
            return country_obj
        return None
    
    def validate_lead_source(self, value):
        if value:  # ✅ Skip validation if empty
            lead_source_obj = Lead_Source.objects.filter(source=value).first()
            if not lead_source_obj:
                raise serializers.ValidationError("Invalid lead source.")
            return lead_source_obj
        return None

    def validate_state(self, value):
        if value:
            state_obj = State.objects.filter(state_name=value).first()
            if not state_obj:
                raise serializers.ValidationError("Invalid state.")
            return state_obj
        return None

    def validate_city(self, value):
        if value:
            city_obj = City.objects.filter(city_name=value).first()
            if not city_obj:
                raise serializers.ValidationError("Invalid city.")
            return city_obj
        return None

    def validate_opportunity_status(self, value):
        opportunity_status_obj = Lead_Status.objects.filter(name=value).first()
        if not opportunity_status_obj:
            raise serializers.ValidationError("Invalid opportunity status.")
        return opportunity_status_obj

    def validate_opportunity_name(self, value):
        opportunity_name_obj = Opportunity_Name.objects.filter(name=value).first()
        if not opportunity_name_obj:
            raise serializers.ValidationError("Invalid Opportunity name.")
        return opportunity_name_obj

