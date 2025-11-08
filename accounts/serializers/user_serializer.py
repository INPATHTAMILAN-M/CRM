from django.contrib.auth.models import User
from rest_framework import serializers
from lead.models import Employee
from accounts.models import UserTarget


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    monthly_target = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]

    def get_phone_number(self, obj):
        try:
            return obj.employee.phone_number
        except Employee.DoesNotExist:
            return None

    def get_monthly_target(self, obj):
        try:
            current_target = UserTarget.objects.filter(user=obj, is_active=True).first()
            if current_target:
                return current_target.target_value
        except Exception:
            pass
        return None

    class Meta:
        model = User
        fields = "__all__"
