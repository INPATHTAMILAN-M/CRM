from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Lead_Status, Log, Task, Task_Assignment, Opportunity, Lead, Contact, Focus_Segment, Log_Stage

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"

class FocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = "__all__"

class LogStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = "__all__"

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_active']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"

class TaskAssignmentSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(allow_null=True, required=False, queryset=User.objects.all(),many=True)
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
    task_type = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time','log_type',
            'log_stage', 'details', 'file', 'created_on', 'is_active', 'task_assignment','task_type'
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
        task_type = validated_data.pop('task_type',None)
        log = super().create(validated_data)

        if log.follow_up_date_time and task_assignment_data:
            task = Task.objects.create(
                contact=log.contact,
                log=log,
                task_date_time=log.follow_up_date_time,
                task_detail=log.details,
                created_by=log.created_by,
                task_creation_type='Automatic',
                task_type = task_type,
            )
            if task_assignment_data and task_assignment_data['assigned_to']:
                    for user_id in task_assignment_data['assigned_to']:
                        Task_Assignment.objects.create(
                            task=task,
                            assigned_to=user_id,
                            assigned_by=log.created_by,
                            assignment_note=task_assignment_data.get('assignment_note', 'Task created automatically'),
                        )

        return log

class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Status
        fields = '__all__'
        
class LogRetrieveSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    lead = LeadSerializer()
    opportunity = OpportunitySerializer()
    task = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'task'
        ]
    
    def get_task(self, obj):
        task = Task.objects.filter(log=obj).first()
        return TaskSerializer(task).data if task else None
    

class LogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active'
        ]

        
class LogListSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    lead = LeadSerializer()
    opportunity = OpportunitySerializer()
    created_by = UserSerializer()
    focus_segment = FocusSegmentSerializer()
    log_stage = LogStageSerializer()
    
    class Meta:
        model = Log
        fields = '__all__'