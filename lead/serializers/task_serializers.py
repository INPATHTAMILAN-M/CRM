from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from django.contrib.auth.models import User

from accounts.models import Log_Stage

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
    class Meta:
        model = Task
        fields = ["contact","log",'task_date_time', 'task_detail', 'is_active','remark','tasktype']
    
    def update(self, instance, validated_data):
        # Check if 'task_date_time' is provided, if not, don't update the task
        if not validated_data.get('task_date_time'):
            return None  # Return None if task_date_time is missing

        # Pop task_assignment data
        task_assignment_data = validated_data.pop('task_assignment', [])

        # Update task fields with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the task instance after updating the fields
        instance.save()

        # Check if task_assignment data was provided in the request
        if task_assignment_data:
            # Clear existing task assignments
            instance.task_assignment.all().delete()  # This will delete all existing assignments for the task

            # Now create new task assignments if data is provided
            for assignment_data in task_assignment_data:
                Task_Assignment.objects.create(
                    task=instance,
                    assigned_to=assignment_data['assigned_to'],
                    assigned_by=self.context['request'].user  # Set the current user as assigned_by
                )

        return instance

class TaskDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()

    class Meta:
        model = Task
        fields = ['id', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 'created_on', 'is_active', 'tasktype','remark']