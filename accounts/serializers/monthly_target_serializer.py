from rest_framework import serializers
from accounts.models import MonthlyTarget
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class MonthlyTargetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'month', 'year', 'target_amount']
        read_only_fields = ['user']