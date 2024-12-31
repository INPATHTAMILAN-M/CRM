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
        fields = '__all__'

class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()
    assignment_details = TaskAssignmentListSerializer(source='task_assignment_set', many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 'created_on', 'is_active', 'tasktype', 'assignment_details']

    # def get_assignment_details(self, obj):
    #     task_assignments = Task_Assignment.objects.filter(task=obj)
    #     return TaskAssignmentListSerializer(task_assignments, many=True).data
    
class TaskCreateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['contact', 'log', 'task_date_time', 'task_detail', 'tasktype', 'task_assignment','remark']

    def create(self, validated_data):
        task_assignment_data = validated_data.pop('task_assignment', [])
        validated_data['created_by'] = self.context['request'].user  # Set created_by to the current user
        task = Task.objects.create(**validated_data)

        # Iterate over the task_assignment list
        for assignment_data in task_assignment_data:
            Task_Assignment.objects.create(
                task=task,
                assigned_to=assignment_data['assigned_to'],  # Set the assigned_to user from the request data
                assigned_by=self.context['request'].user  # Always set assigned_by to the current user
            )
        
        return task

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["contact","log",'task_date_time', 'task_detail', 'is_active','remark','tasktype']

class TaskDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()

    class Meta:
        model = Task
        fields = ['id', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 'created_on', 'is_active', 'tasktype','remark']