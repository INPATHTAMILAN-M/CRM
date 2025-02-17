from rest_framework import serializers
from ..models import TaskConversationLog

class TaskConversationLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = '__all__'

    def create(self, validated_data):
        task = self.initial_data.get('task', None)
        if task and  self.request.user in [task.task_task_assignments.assigned_to,
                                           task.task_task_assignments.assigned_by]:
            validated_data['created_by'] = self.request.user

            return TaskConversationLog.objects.create(**validated_data)
        
        raise serializers.ValidationError("You are not authorized to create a conversation log for this task.")

class TaskConversationLogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConversationLog
        fields = '__all__'

    def update(self, instance, validated_data):
        task = instance.task
        if task and  self.request.user in [task.task_task_assignments.assigned_to,
                                           task.task_task_assignments.assigned_by]:
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