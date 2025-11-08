from django.contrib.auth.models import User, Group
from rest_framework import serializers
from lead.models import Employee
from accounts.models import UserTarget

class UserTargetListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTarget
        fields = ['id', 'user', 'target', 'is_active', 'created_at', 'updated_at']
        
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)
    phone_number = serializers.SerializerMethodField()
    monthly_target = UserTargetListSerializer(source='user_target', read_only=True)

    def get_phone_number(self, obj):
        try:
            return obj.employee.phone_number
        except Employee.DoesNotExist:
            return None

    class Meta:
        model = User
        fields = "__all__"
