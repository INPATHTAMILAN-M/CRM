from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from lead.models import Employee
from accounts.models import UserTarget

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class UserTargetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'is_active', 'created_at', 'updated_at']

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for GET requests - returns full details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    phone_number = serializers.SerializerMethodField()
    monthly_target = UserTargetListSerializer(source='user_target', read_only=True)

    def get_phone_number(self, obj):
        try:
            return obj.employee.phone_number
        except Employee.DoesNotExist:
            return None

    class Meta:
        model = User
        exclude = ['password','user_permissions','is_superuser','last_login','is_staff']
        # fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 
        #          'full_name', 'groups', 'phone_number', 'monthly_target']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for POST requests"""
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'groups', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        user = User.objects.create_user(**validated_data)
        if groups:
            user.groups.set(groups)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for PATCH requests"""
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'groups', 'is_active']
        
class UserDeleteSerializer(serializers.ModelSerializer):
    """Serializer for DELETE requests"""
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']
