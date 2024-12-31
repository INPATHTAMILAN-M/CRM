from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from django.contrib.auth.models import User

from ..models import Task, Contact, Log, Task_Assignment, Lead

class LeadContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    lead = LeadContactSerializer()
    class Meta:
        model = Contact
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task_Assignment
        fields = ['assigned_to',"assignment_note"]

class TaskAssignmentListSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer()
    class Meta:
        model = Task_Assignment
        fields = ['id','assigned_to',"assignment_note"]

class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()
    assigned_to = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 'created_on', 'is_active', 'tasktype', 'assigned_to']

    def get_assigned_to(self, obj):
        # Get all Task_Assignment records related to this task
        task_assignments = Task_Assignment.objects.filter(task=obj, is_active=True)
        # Serialize the assignment data using TaskAssignmentSerializer
        return TaskAssignmentListSerializer(task_assignments, many=True).data
    
class TaskCreateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(required=False)
    class Meta:
        model = Task
        fields = ['contact', 'log', 'task_date_time', 'task_detail', 'tasktype', 'task_assignment','remark']

    def create(self, validated_data):
        task_assignment_data = validated_data.pop('task_assignment', None)
        validated_data['created_by'] = self.context['request'].user
        task = Task.objects.create(**validated_data)

        if task_assignment_data:
            Task_Assignment.objects.create(task=task,assigned_by=task.created_by,**task_assignment_data)
        return task

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["contact","log",'task_date_time', 'task_detail', 'is_active','remark']

class TaskDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()

    class Meta:
        model = Task
        fields = ['id', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 'created_on', 'is_active', 'tasktype','remark']