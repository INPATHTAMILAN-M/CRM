from django.contrib.auth.models import User, Group
from rest_framework import serializers
from lead.models import UserProfile, Department, Designation
from accounts.models import UserTarget, Country

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class UserTargetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'is_active', 'created_at', 'updated_at']

class UserProfileSerializer(serializers.ModelSerializer):
    """Nested serializer for UserProfile"""
    country_code = serializers.StringRelatedField()
    department = serializers.StringRelatedField()
    designation = serializers.StringRelatedField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'country_code', 'phone_number', 'department', 
            'designation', 'profile_photo', 'gender', 
            'blood_group', 'address', 'is_active'
        ]

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for GET requests - returns full details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    userprofile = UserProfileSerializer(read_only=True)
    monthly_target = UserTargetListSerializer(source='user_target', read_only=True)

    class Meta:
        model = User
        exclude = ['password','user_permissions','is_superuser','last_login','is_staff']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a user with their profile"""
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    
    # UserProfile fields
    country_code = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), write_only=True)
    phone_number = serializers.CharField(max_length=255, write_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), 
        write_only=True, 
        required=False, 
        allow_null=True
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(), 
        write_only=True, 
        required=False, 
        allow_null=True
    )
    profile_photo = serializers.ImageField(write_only=True, required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], 
        write_only=True
    )
    blood_group = serializers.ChoiceField(
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
                 ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], 
        write_only=True
    )
    address = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'groups', 'is_active',
            # UserProfile fields
            'country_code', 'phone_number', 'department', 'designation', 
            'profile_photo', 'gender', 'blood_group', 'address'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create user and their profile in a single transaction"""
        # Extract profile data
        profile_data = {
            'country_code': validated_data.pop('country_code'),
            'phone_number': validated_data.pop('phone_number'),
            'department': validated_data.pop('department', None),
            'designation': validated_data.pop('designation', None),
            'profile_photo': validated_data.pop('profile_photo', None),
            'gender': validated_data.pop('gender'),
            'blood_group': validated_data.pop('blood_group'),
            'address': validated_data.pop('address'),
        }
        
        # Extract groups
        groups = validated_data.pop('groups', [])
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Set groups if provided
        if groups:
            user.groups.set(groups)
        
        # Create user profile
        UserProfile.objects.create(user=user, **profile_data)
        
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for PATCH requests - updates user and profile"""
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    
    # UserProfile fields (optional for update)
    country_code = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), 
        write_only=True, 
        required=False
    )
    phone_number = serializers.CharField(max_length=255, write_only=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), 
        write_only=True, 
        required=False, 
        allow_null=True
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(), 
        write_only=True, 
        required=False, 
        allow_null=True
    )
    profile_photo = serializers.ImageField(write_only=True, required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], 
        write_only=True,
        required=False
    )
    blood_group = serializers.ChoiceField(
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
                 ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], 
        write_only=True,
        required=False
    )
    address = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'groups', 'is_active',
            # UserProfile fields
            'country_code', 'phone_number', 'department', 'designation', 
            'profile_photo', 'gender', 'blood_group', 'address'
        ]
    
    def update(self, instance, validated_data):
        """Update user and their profile"""
        # Extract profile data
        profile_fields = ['country_code', 'phone_number', 'department', 'designation', 
                         'profile_photo', 'gender', 'blood_group', 'address']
        profile_data = {key: validated_data.pop(key) for key in profile_fields if key in validated_data}
        
        # Extract groups
        groups = validated_data.pop('groups', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update groups if provided
        if groups is not None:
            instance.groups.set(groups)
        
        # Update profile if profile data is provided
        if profile_data:
            try:
                profile = instance.userprofile
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=instance, **profile_data)
        
        return instance
        
class UserDeleteSerializer(serializers.ModelSerializer):
    """Serializer for DELETE requests"""
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']
