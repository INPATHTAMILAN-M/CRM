from django.http import JsonResponse
from ..models import Contact  # Import the Contact model
from lead.serializers.contactserializer import ContactSerializer # Import the serializer

def get_contact_detail(contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)  # Fetch the contact by ID
        serializer = ContactSerializer(contact)
        return JsonResponse(serializer.data, status=200)
    except Contact.DoesNotExist:
        return JsonResponse({"message": "Contact not found"}, status=404)
