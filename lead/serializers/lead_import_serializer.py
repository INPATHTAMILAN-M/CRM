from rest_framework import serializers
from accounts.models import User
from lead.models import (
    Lead, Opportunity_Status, Contact_Status, Contact, 
    Country, State, City, Opportunity_Name
)

class LeadImportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=50)
    phone_number = serializers.RegexField(regex=r'^\d{10}$', error_messages={
        'invalid': 'Phone number must be a 10-digit number without spaces.'
    })
    remark = serializers.CharField(max_length=500, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    opportunity_name = serializers.CharField(max_length=200)
    lead_owner = serializers.CharField(max_length=100)
    opportunity_status = serializers.CharField(max_length=50)
    status_date = serializers.DateTimeField(format="%Y-%m-%d", input_formats=['%Y-%m-%d'])

    def validate_company_name(self, value):
        if Lead.objects.filter(name=value).exists():
            raise serializers.ValidationError("Company name already exists.")
        return value

    def validate_phone_number(self, value):
        if Contact.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_status(self, value):
        status_obj = Contact_Status.objects.filter(status=value).first()
        if not status_obj:
            raise serializers.ValidationError("Invalid status.")
        return status_obj

    def validate_country(self, value):
        country_obj = Country.objects.filter(country_name=value).first()
        if not country_obj:
            raise serializers.ValidationError("Invalid country.")
        return country_obj

    def validate_state(self, value):
        state_obj = State.objects.filter(state_name=value).first()
        if not state_obj:
            raise serializers.ValidationError("Invalid state.")
        return state_obj

    def validate_city(self, value):
        city_obj = City.objects.filter(city_name=value).first()
        if not city_obj:
            raise serializers.ValidationError("Invalid city.")
        return city_obj

    def validate_opportunity_status(self, value):
        opportunity_status_obj = Opportunity_Status.objects.filter(name=value).first()
        if not opportunity_status_obj:
            raise serializers.ValidationError("Invalid opportunity status.")
        return opportunity_status_obj
    
    def validate_opportunity_name(self, value):
        opportunity_name_obj = Opportunity_Name.objects.filter(name=value).first()
        if not opportunity_name_obj:
            raise serializers.ValidationError("Invalid Opportunity name.")
        return opportunity_name_obj

    def validate_lead_owner(self, value):
        user = User.objects.filter(username=value).first()
        if not user:
            raise serializers.ValidationError("Invalid lead owner. User not found.")
        return user
