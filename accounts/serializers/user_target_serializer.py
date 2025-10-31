from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import UserTarget


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user basic info"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    group = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'group']
    
    def get_group(self, obj):
        if obj.groups.exists():
            return {"id": obj.groups.first().id, "name": obj.groups.first().name}
        return None


class UserTargetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserTarget"""
    class Meta:
        model = UserTarget
        fields = ['user', 'target']
    
    def validate(self, data):
        user = data.get('user')
        
        # Prevent admin users from having targets
        if user.groups.filter(name__iexact='admin').exists():
            raise serializers.ValidationError("Cannot create target for admin users.")
        
        # Ensure user doesn't already have a target
        if UserTarget.objects.filter(user=user).exists():
            raise serializers.ValidationError("A target already exists for this user. Use update instead.")
        
        return data


class UserTargetUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating UserTarget"""
    class Meta:
        model = UserTarget
        fields = ['target']


class UserTargetListSerializer(serializers.ModelSerializer):
    """Serializer for listing UserTargets"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'created_at', 'updated_at']


class UserTargetRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving single UserTarget with full details"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'created_at', 'updated_at']