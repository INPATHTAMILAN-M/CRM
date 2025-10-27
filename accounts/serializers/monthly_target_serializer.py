from rest_framework import serializers
from accounts.models import MonthlyTarget
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'group']

    def get_group(self, obj):
        return {"id": obj.groups.first().id, "name": obj.groups.first().name} if obj.groups.exists() else None

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