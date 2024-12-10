from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]

    class Meta:
        model = User
        fields = ['id', 'full_name', 'groups']
