from rest_framework import serializers
from ..models import Log
class LogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

    # Validating to ensure contact is provided
    def validate_contact(self, value):
        if not value:
            raise serializers.ValidationError("Contact is required.")
        return value



class LogReadSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    focus_segment = serializers.SerializerMethodField()
    log_stage = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    logtype = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = '__all__'

    def get_contact(self, obj):
        return {
            'id': obj.contact.id,
            'name': obj.contact.name
        } if obj.contact else None

    def get_focus_segment(self, obj):
        return {
            'id' : obj.focus_segment.id,
            'name': obj.focus_segment.focus_segment
        } if obj.focus_segment else None

    def get_log_stage(self, obj):
        return {
            'id' : obj.log_stage.id,
            'stage' : obj.log_stage.stage
        } if obj.log_stage else None

    def get_created_by(self, obj):
        return {
            'id' : obj.created_by.id,
            'username' : obj.created_by.username
        } if obj.created_by else None
    
    def get_logtype(self, obj):
        return {
            'code': obj.logtype,
            'label': obj.get_logtype_display()
        }
    def get_file_url(self, obj):
        if obj.file:
            file_url = obj.file.url
            domain = "http://121.200.52.133:8000/"
            return f"{domain}{file_url}"
        return None