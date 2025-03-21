from rest_framework import serializers
from rest_framework.routers import DefaultRouter
from django.contrib.auth.models import User
from django.db.models import Q
from accounts.models import Log_Stage

from ..models import Lead_Status, Notification, Task, Contact, Log, Task_Assignment, Lead, TaskConversationLog

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
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        # Get the group names from the groups associated with the user
        return [group.name for group in obj.groups.all()]
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name','groups', 'email', 'is_active']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task_Assignment
        fields = ['assigned_to',"assignment_note"]

class TaskAssignmentListSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer()
    assigned_by = UserSerializer()

    class Meta:
        model = Task_Assignment
        fields = ['assigned_to', 'assigned_by', 'assigned_on', 
                  'assignment_note', 'is_active']

        
class TaskListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()
    reply_counts = serializers.SerializerMethodField()
    has_new_message = serializers.SerializerMethodField()
    can_reply = serializers.SerializerMethodField()
    assignment_details = serializers.SerializerMethodField()
    task_task_assignments = TaskAssignmentListSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'log', 'task_date_time', 'task_detail', 
                  'created_by', 'created_on', 'is_active', 'task_creation_type','task_type',
                  'reply_counts', 'has_new_message','can_reply','assignment_details','task_task_assignments']

    def get_assignment_details(self, obj):
        task_assignments = obj.task_task_assignments.all()
        return TaskAssignmentListSerializer(task_assignments, many=True).data
     
    def get_reply_counts(self, obj):
        return TaskConversationLog.objects.filter(task=obj).exclude(seen_by=self.context['request'].user).count()    
    
    def get_has_new_message(self, obj):
        return TaskConversationLog.objects.filter(task=obj).exclude(seen_by=self.context['request'].user).exists()
    
    def get_can_reply(self, obj):
        return Task_Assignment.objects.filter(Q(assigned_to=self.context['request'].user) | Q(assigned_by=self.context['request'].user), task=obj).exists()
        
    
    


class TaskCreateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['id','contact', 'log', 'task_date_time', 'task_detail', 'task_type', 'task_assignment','remark']

    def create(self, validated_data):
        # Check if 'task_date_time' is provided
        if not validated_data.get('task_date_time'):
            return None  # Return None instead of raising an error

        task_assignment_data = validated_data.pop('task_assignment', [])
        print("task")
        validated_data['created_by'] = self.context['request'].user  
        validated_data['task_creation_type'] = 'Manual'
        task = Task.objects.create(**validated_data)
        # Iterate over the task_assignment list
        for assignment_data in task_assignment_data:
            assigned_by = assignment_data.get('assigned_by', self.context['request'].user)
            Task_Assignment.objects.create(
                task=task,
                assigned_to=assignment_data['assigned_to'],  # Set the assigned_to user from the request data
                assigned_by=assigned_by  # Always set assigned_by to the current user
            )
           
            Notification.objects.create(
                task=task,
                receiver=assignment_data['assigned_to'],
                message=f"{assigned_by.first_name} {assigned_by.last_name} assigned a new Task.",
                assigned_by=self.context['request'].user,
                type='Task'
            )
        return task
    
class TaskUpdateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(many=True, required=False)
    class Meta:
        model = Task
        fields = ['id', "contact", "log", 'task_date_time', 'task_detail',
                  'is_active', 'remark', 'task_type', 'task_assignment']

    def update(self, instance, validated_data):
        # Get the task assignment data from the request
        task_assignment_data = validated_data.pop('task_assignment', [])

        # Update the Task fields first
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Task_Assignment.objects.filter(task=instance).delete()
        # Clear existing task assignments before adding new ones
        if task_assignment_data:
            # Create new task assignments from the provided data
            for assignment in task_assignment_data:
                if not Task_Assignment.objects.filter(task=instance, assigned_to=assignment['assigned_to']).exists():
                    Task_Assignment.objects.create(
                        task=instance,
                        assigned_to=assignment['assigned_to'],
                        assigned_by=self.context['request'].user  # Set the current user as assigned_by
                    )
                    Notification.objects.create(
                    task=instance,
                    receiver_id=assignment['assigned_to'],
                    message=f"{self.context['request'].user.first_name} {self.context['request'].user.last_name} assigned a new Task.",
                    assigned_by=self.context['request'].user,
                    type='Task'
                )

        return instance

class TaskConversationLogSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    class Meta:
        model = TaskConversationLog
        fields = '__all__'

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class TaskDetailSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    log = LogSerializer()
    created_by = UserSerializer()
    task_conversation_logs = TaskConversationLogSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'contact', 'log', 'task_date_time', 'task_detail', 'created_by', 
                  'created_on', 'is_active', 'task_type', 'remark','task_conversation_logs']