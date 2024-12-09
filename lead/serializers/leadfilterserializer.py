from rest_framework import serializers
from ..models import Lead, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag']

class LeadFilterSerializer(serializers.ModelSerializer):
    focus_segment = serializers.StringRelatedField()
    market_segment = serializers.StringRelatedField()
    state = serializers.StringRelatedField()
    country = serializers.StringRelatedField()
    lead_owner = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()
    tags = TagSerializer(many=True)
    
    # New field for vertical id and name
    vertical = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id", "name", "focus_segment", "market_segment", "state", "country", 
            "created_on", "annual_revenue", "company_number", "company_email", 
            "company_website", "fax", "tags", "lead_owner", "created_by", 
            "is_active", "vertical"
        ]

    def get_vertical(self, obj):
        # Get the vertical info from the related focus_segment
        if obj.focus_segment and obj.focus_segment.vertical:
            return {
                "id": obj.focus_segment.vertical.id,
                "name": obj.focus_segment.vertical.vertical
            }
        return None  # In case there's no vertical associated
