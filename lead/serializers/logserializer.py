from rest_framework import serializers
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

# class TaskSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = ['task_date_time', 'task_detail']

# class TaskAssignmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task_Assignment
#         fields = ['assigned_to', 'assignment_note']

class PostLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype'
        ]

    def validate(self, data):
        lead = data.get('lead')
        opportunity = data.get('opportunity')

        if not lead and not opportunity:
            raise serializers.ValidationError("Either lead or opportunity must be provided")
        if lead and opportunity:
            raise serializers.ValidationError("Cannot provide both lead and opportunity")
            
        return data
    

    def create(self, validated_data):
        # Create the Log instance
        log = super().create(validated_data)

        if log.follow_up_date_time:
            # Create the Task associated with the Log
            task = Task.objects.create(
                contact=log.contact,
                log=log,
                task_date_time=log.follow_up_date_time,
                task_detail=log.details,
                created_by=log.created_by,
                tasktype='Automatic',
            )

            # Create Task Assignment
            Task_Assignment.objects.create(
                task=task,
                assigned_to=log.created_by,
                assigned_by=log.created_by,
                assignment_note='Task created automatically',
            )

        return log

class GetLogSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    lead = LeadSerializer()
    opportunity = OpportunitySerializer()
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype'
        ]

class ListLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            'id', 'contact', 'lead', 'opportunity', 'focus_segment', 'follow_up_date_time',
            'log_stage', 'details', 'file', 'created_by', 'created_on', 'is_active', 'logtype'
        ]