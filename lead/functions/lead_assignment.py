from django.http import JsonResponse
from django.contrib.auth.models import User
from ..models import Lead, Lead_Assignment
from ..serializers.leadassignserializer import LeadAssignmentSerializer
import json

def post_lead_assignment(request, lead_id):
    # assigned_by_user = User.objects.get(id=3)
    try:
        lead = Lead.objects.get(id=lead_id)
    except Lead.DoesNotExist:
        return JsonResponse({"message": "Lead not found"}, status=404)
    
    data = json.loads(request.body)
    assigned_to_ids = data.get('assigned_to')  # Expecting list of user IDs

    if not assigned_to_ids:
        return JsonResponse({"message": "No employees selected"}, status=400)

    # Iterate through selected users and create Lead_Assignment records
    for user_id in assigned_to_ids:
        try:
            user = User.objects.get(id=user_id)
            Lead_Assignment.objects.create(lead=lead, assigned_to=user, assigned_by=request.user)  # assigned_by=assigned_by_user (for hard-coded checking)
        except User.DoesNotExist:
            return JsonResponse({"message": f"User {user_id} not found"}, status=404)

    return JsonResponse({"message": "Lead assigned successfully"}, status=201)
