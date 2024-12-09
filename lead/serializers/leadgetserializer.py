from rest_framework import serializers
from lead.models import Lead, Focus_Segment, Market_Segment, State, Country, Tag, User

class FocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = ['id', 'focus_segment', 'vertical']

class MarketSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market_Segment
        fields = ['id', 'market_segment']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'state_name']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'focus_segment', 'market_segment', 'state', 'country', 'created_on',
            'annual_revenue', 'company_number', 'company_email', 'company_website', 'fax', 
            'tags', 'lead_owner', 'created_by', 'is_active'
        ]

    def to_representation(self, instance):
        # Call the parent class's to_representation method
        representation = super().to_representation(instance)
        
        # Construct the desired format
        return {
            "id": representation['id'],
            "name": representation['name'],
            "focus_segment": {
                "id": representation['focus_segment']['id'],
                "focus_segment": representation['focus_segment']['focus_segment'],
            },
            "vertical": {
                "id": representation['focus_segment']['vertical']['id'],
                "vertical": representation['focus_segment']['vertical']['vertical'],
            },
            "market_segment": {
                "id": representation['market_segment']['id'],
                "market_segment": representation['market_segment']['market_segment'],
            },
            "state": {
                "id": representation['state']['id'] if representation['state'] else None,
                "state_name": representation['state']['state_name'] if representation['state'] else None,
            },
            "country": {
                "id": representation['country']['id'],
                "country_name": representation['country']['country_name'],
            },
            "created_on": representation['created_on'],
            "annual_revenue": representation['annual_revenue'],
            "company_number": representation['company_number'],
            "company_email": representation['company_email'],
            "company_website": representation['company_website'],
            "fax": representation['fax'],
            "tags": [{"id": tag['id'], "tag": tag['tag']} for tag in representation['tags']],
            "lead_owner": {
                "id": representation['lead_owner']['id'],
                "username": representation['lead_owner']['username'],
            },
            "created_by": {
                "id": representation['created_by']['id'],
                "username": representation['created_by']['username'],
            },
            "is_active": representation['is_active'],
        }
