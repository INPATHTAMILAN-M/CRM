from rest_framework import viewsets
from ..models import Contact
from ..serializers.contact_serializer import ContactSerializer
from ..filters.contact_filter import ContactFilter  # Import the filter class

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filterset_class = ContactFilter 

    
    ordering_fields = ['name', 'created_on'] 
    ordering = ['name'] 
