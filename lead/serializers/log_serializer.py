from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Log, Task, Task_Assignment, Opportunity, Lead, Contact

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

class TaskAssignmentSerializer(serializers.ModelSerializer):
    # assigned_to = serializers.PrimaryKeyRelatedField(allow_null=True, required=False, queryset=User.objects.all())
    class Meta:
        model = Task_Assignment
        fields = ['assigned_to', 'assignment_note']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'contact', 'log', 'task_date_time', 'task_detail', 
            'created_by', 'created_on', 'is_active', 'tasktype'
        ]


class LogCreateSerializer(serializers.ModelSerializer):
    task_assignment = TaskAssignmentSerializer(write_only=True, required=False)
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_on', 'is_active', 'logtype', 'task_assignment'
        ]

    def validate_follow_up_date_time(self, value):
        if value and not self.initial_data.get('task_assignment'):
            raise serializers.ValidationError("Task Assignment is required if follow_up_date_time is provided.")
        return value

    def validate(self, data):
        lead = data.get('lead')
        opportunity = data.get('opportunity')

        if not bool(lead) ^ bool(opportunity):  # XOR logic for exclusive selection
            raise serializers.ValidationError("Provide exactly one of 'lead' or 'opportunity'.")
        return data

    def create(self, validated_data):
        task_assignment_data = validated_data.pop('task_assignment', None)
        validated_data['created_by'] = self.context['request'].user
        log = super().create(validated_data)

        if log.follow_up_date_time and task_assignment_data:
            task = Task.objects.create(
                contact=log.contact,
                log=log,
                task_date_time=log.follow_up_date_time,
                task_detail=log.details,
                created_by=log.created_by,
                tasktype='Automatic',
            )
            Task_Assignment.objects.create(
                task=task,
                assigned_to=task_assignment_data['assigned_to'],
                assigned_by=log.created_by,
                assignment_note=task_assignment_data.get('assignment_note', 'Task created automatically'),
            )

        return log
  

    
class LogRetrieveSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    lead = LeadSerializer()
    opportunity = OpportunitySerializer()
    task = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype', 'task'
        ]
    
    def get_task(self, obj):
        task = Task.objects.filter(log=obj).first()
        return TaskSerializer(task).data if task else None
    

class LogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype'
        ]

class LogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype'
        ]