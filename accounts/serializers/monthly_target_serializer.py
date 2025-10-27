from rest_framework import serializers
from accounts.models import MonthlyTarget
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class MonthlyTargetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target_amount', 'created_at']
        read_only_fields = ['created_at']

class MonthlyTargetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target_amount', 'created_at']