from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from ..models import UserTarget, MonthlyTarget


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
    
    def create(self, validated_data):
        """Create UserTarget and corresponding MonthlyTarget for current month"""
        user = validated_data['user']
        target_amount = validated_data['target']
        
        # Create UserTarget
        user_target = UserTarget.objects.create(
            user=user,
            target=target_amount,
            is_active=True,
        )
        
        # Create MonthlyTarget for current month
        current_date = datetime.now()
        MonthlyTarget.objects.get_or_create(
            user=user,
            month=current_date.month,
            year=current_date.year,
            defaults={'target_amount': target_amount}
        )
        
        return user_target


class UserTargetUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating UserTarget"""
    class Meta:
        model = UserTarget
        fields = ['target','is_active']
    
    def update(self, instance, validated_data):
        """Update UserTarget and corresponding MonthlyTarget records"""
        new_target = validated_data.get('target', instance.target)
        is_active = validated_data.get('is_active', instance.is_active)
        instance.is_active = is_active
        # Update the UserTarget
        instance.target = new_target
        instance.save()
        
        # Get month and year from when the instance was last updated
        updated_at = instance.updated_at
        updated_user = instance.user
        update_month = updated_at.month
        update_year = updated_at.year
        
        # Update MonthlyTarget for current month/year and all future months
        # Build a filter for all months >= update_month in update_year and all future years
        
        # Filter: (year = update_year AND month >= update_month) OR (year > update_year)
        filter_condition = Q(
            user=updated_user
        ) & (
            Q(year=update_year, month__gte=update_month) | Q(year__gt=update_year)
        )
        
        # Update all existing MonthlyTargets that match the condition
        MonthlyTarget.objects.filter(filter_condition).update(target_amount=new_target)
        
        # Also ensure the current month/year has a MonthlyTarget (in case it doesn't exist)
        MonthlyTarget.objects.update_or_create(
            user=updated_user,
            month=update_month,
            year=update_year,
            defaults={'target_amount': new_target}
        )
        
        return instance


class UserTargetListSerializer(serializers.ModelSerializer):
    """Serializer for listing UserTargets"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'is_active', 'created_at', 'updated_at']


class UserTargetRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for retrieving single UserTarget with full details"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'is_active', 'created_at', 'updated_at']