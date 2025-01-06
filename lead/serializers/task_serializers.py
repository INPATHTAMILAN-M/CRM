from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from django.contrib.auth.models import User

from accounts.models import Log_Stage

from ..models import Lead_Status, Task, Contact, Log, Task_Assignment, Lead

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
    assigned_by = UserSerializer()

    class Meta:
        model = Task_Assignment
        fields = ['assigned_to', 'assigned_by', 'assigned_on', 'assignment_note', 'is_active']

        
class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()
    assignment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'log', 'task_date_time', 'task_detail', 
                  'created_by', 'created_on', 'is_active', 'tasktype', 'assignment_details']

    def get_assignment_details(self, obj):
        task_assignments = obj.task_task_assignments.all()
        return TaskAssignmentListSerializer(task_assignments, many=True).data
    
    
    
    
    

class TaskCreateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['id','contact', 'log', 'task_date_time', 'task_detail', 'tasktype', 'task_assignment','remark']

    def create(self, validated_data):
        # Check if 'task_date_time' is provided
        if not validated_data.get('task_date_time'):
            return None  # Return None instead of raising an error

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
    task_assignment = TaskAssignmentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['id', "contact", "log", 'task_date_time', 'task_detail',
                  'is_active', 'remark', 'tasktype', 'task_assignment']

    def update(self, instance, validated_data):
        # Get the task assignment data from the request
        task_assignment_data = validated_data.pop('task_assignment', [])

        # Update the Task fields first
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        Task_Assignment.objects.filter(task=instance).delete()
        # Clear existing task assignments before adding new ones
        if task_assignment_data:
            # Create new task assignments from the provided data
            for assignment in task_assignment_data:
                Task_Assignment.objects.create(
                    task=instance,
                    assigned_to=assignment['assigned_to'],
                    assigned_by=self.context['request'].user  # Set the current user as assigned_by
                )

        return instance

class TaskDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()

    class Meta:
        model = Task
        fields = ['id', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 
                  'created_on', 'is_active', 'tasktype', 'remark']