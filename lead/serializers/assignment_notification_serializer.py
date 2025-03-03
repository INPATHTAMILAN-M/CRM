from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Q

from ..models import Task, Contact, Log, Task_Assignment, Lead, TaskConversationLog

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

    class Meta:
        model = Task
        fields = ['id', 'remark', 'contact', 'log', 'task_date_time', 'task_detail', 
                  'created_by', 'created_on', 'is_active', 'task_creation_type','task_type',
                  'reply_counts', 'has_new_message','can_reply','assignment_details']

    def get_assignment_details(self, obj):
        task_assignments = obj.task_task_assignments.all()
        return TaskAssignmentListSerializer(task_assignments, many=True).data
     
    def get_reply_counts(self, obj):
        return TaskConversationLog.objects.filter(task=obj).exclude(seen_by=self.context['request'].user).count()    
    
    def get_has_new_message(self, obj):
        return TaskConversationLog.objects.filter(task=obj).exclude(seen_by=self.context['request'].user).exists()
    
    def get_can_reply(self, obj):
        return Task_Assignment.objects.filter(Q(assigned_to=self.context['request'].user) | Q(assigned_by=self.context['request'].user), task=obj).exists()
        