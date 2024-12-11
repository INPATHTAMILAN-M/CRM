
from rest_framework import serializers
from lead.models import Notification

class NotificationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'message', 'created_at', 'updated_at']
        
class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['user', 'message']

class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']

