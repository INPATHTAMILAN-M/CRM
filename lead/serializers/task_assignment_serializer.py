from rest_framework import serializers
from ..models import Task_Assignment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    assigned_by = UserSerializer()
    assigned_to = UserSerializer()
    class Meta:
        model = Task_Assignment
        fields = ['id', 'task', 'assigned_to', 'assigned_by', 'assigned_on', 'assignment_note', 'is_active']
