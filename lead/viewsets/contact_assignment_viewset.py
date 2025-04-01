from rest_framework import viewsets
from lead.custom_pagination import Paginator
from rest_framework.permissions import IsAuthenticated
from ..models import Contact_Assignment

from ..serializers.contact_assignment import (
    ContactAssignmentCreateSerializer,
    ContactAssignmentUpdateSerializer,
    ContactAssignmentRetrieveSerializer,
    ContactAssignmentListSerializer
)

class ContactAssignmentViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Contact_Assignment instances.
    """
    queryset = Contact_Assignment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactAssignmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContactAssignmentUpdateSerializer
        elif self.action == 'retrieve':
            return ContactAssignmentRetrieveSerializer
        elif self.action == 'list':
            return ContactAssignmentListSerializer
        return super().get_serializer_class()