from rest_framework import serializers
from ..models import Notification, Task_Assignment, TaskConversationLog, Task
from django.contrib.auth.models import User
from django.db.models import Q

class TaskConversationLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = ['task', 'message']
 
    def create(self, validated_data):
        task_id = self.initial_data.get('task', None)
        
        task = Task.objects.filter(id=task_id).first()
        if not task:
            raise serializers.ValidationError("Task not found.")
        if task.task_task_assignments.filter(
            Q(assigned_to=self.context['request'].user) | Q(assigned_by=self.context['request'].user)
        ).exists():
            validated_data['created_by'] = self.context['request'].user
            instance = TaskConversationLog.objects.create(**validated_data)
            instance.seen_by.set([self.context['request'].user])
            assigned_users = Task_Assignment.objects.filter(task=instance.task).values_list('assigned_to', flat=True)
            for user_id in assigned_users:
                Notification.objects.create(
                    conversation=instance,
                    receiver_id=user_id,
                    message=f"You received message from {self.context['request'].user.first_name} {self.context['request'].user.last_name}.",
                    type = "Conversation"
                )
            return instance
            
        raise serializers.ValidationError("You are not authorized to create a conversation log for this task.")

class TaskConversationLogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = ['task', 'message']

    def update(self, instance, validated_data):
        task = instance.task
        task_id = self.initial_data.get('task', None)
        
        task = Task.objects.filter(id=task_id).first()
        if not task:
            raise serializers.ValidationError("Task not found.")
        if task.task_task_assignments.filter(
            Q(assigned_to=self.context['request'].user) | Q(assigned_by=self.context['request'].user)
        ).exists():
            assigned_users = Task_Assignment.objects.filter(task=instance.task).values_list('assigned_to', flat=True)
            for user_id in assigned_users:
                Notification.objects.create(
                    conversation=instance,
                    receiver_id=user_id,
                    message=f"You received message from {self.context['request'].user.first_name} {self.context['request'].user.last_name}.",
                    type = "Conversation"
                )
            return super().update(instance, validated_data)
        
        raise serializers.ValidationError("You are not authorized to update this conversation log.")

class TaskConversationLogRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username',  'first_name', 'last_name', 'email', 'is_active']

class TaskConversationLogListSerializer(serializers.ModelSerializer):
    is_viewed = serializers.SerializerMethodField()
    created_by = UserSerializer()

    class Meta:
        model = TaskConversationLog
        fields = ['id', 'task', 'message', 'created_by', 'created_on', 'seen_by', 'is_viewed']


    def get_is_viewed(self, obj):
        """Return True if the logged-in user has viewed this log"""
        request = self.context.get('request')
        if request:
            return obj.is_viewed(request.user)
        return False