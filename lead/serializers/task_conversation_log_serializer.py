from rest_framework import serializers
from ..models import TaskConversationLog, Task
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
            return TaskConversationLog.objects.create(**validated_data)

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
            return super().update(instance, validated_data)
        
        raise serializers.ValidationError("You are not authorized to update this conversation log.")

class TaskConversationLogRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = '__all__'


class TaskConversationLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = '__all__'