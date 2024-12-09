from rest_framework import serializers
from ..models import Task, Task_Assignment

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class GetTaskSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    log = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    tasktype = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'


    def get_contact(self, obj):
            return {
                'id' : obj.contact.id,
                'name': obj.contact.name,
                'lead_id' : obj.contact.lead.id,
                'lead_name' : obj.contact.lead.name
            } if obj.contact else None
    
    def get_log(self, obj):
        return {
            'id' : obj.log.id,
            'log' : obj.log.details
        } if obj.log else None
    
    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'username' : obj.created_by.username
        } if obj.created_by else None
    
    def get_tasktype(self, obj):
        return {
            'code' : obj.tasktype,
            'label' : obj.get_tasktype_display()
        }
    # def get_assigned_to(self, obj):
    #     # Retrieve assigned users from Task_Assignment
    #     assignments = Task_Assignment.objects.filter(task=obj, is_active=True)
    #     assigned_users = [
    #         {
    #             'id': assignment.assigned_to.id,
    #             'assigned_to': assignment.assigned_to.username
    #         }
    #         for assignment in assignments if assignment.assigned_to
    #     ]
    #     return assigned_users if assigned_users else None


    def get_assigned_to(self, obj):
        assignments = Task_Assignment.objects.filter(task=obj, is_active=True)
        assigned_users = []
        added_user_ids = set()  # Track unique user IDs

        for assignment in assignments:
            user_id = assignment.assigned_to.id
            if user_id not in added_user_ids:
                # Only add unique users to the list
                assigned_users.append({
                    'id': user_id,
                    'username': assignment.assigned_to.username
                })
                added_user_ids.add(user_id)  # Mark this user as added

        return assigned_users