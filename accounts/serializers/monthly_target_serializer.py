from rest_framework import serializers
from accounts.models import MonthlyTarget


class MonthlyTargetSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = MonthlyTarget
        fields = ['id', 'user', 'user_name', 'user_full_name', 'month', 'year', 'target_amount']
        read_only_fields = ['user_name', 'user_full_name']