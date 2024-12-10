from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Contact
from ..serializers.contact_serializer import ContactSerializer, PostContactSerializer
from ..paginations.contact_pagination import ContactPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.contact_filter import ContactFilter

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()  # Define the queryset
    serializer_class = ContactSerializer  # Define the serializer class
    permission_classes = [IsAuthenticated]  # Set permission classes to ensure the user is authenticated
    pagination_class = ContactPagination  # Set custom pagination class
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter

    def get_serializer_class(self):
        # Return a different serializer for create (POST) operation
        if self.action == 'create':
            return PostContactSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # Override the perform_create method to add the 'created_by' field
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Override the destroy method to deactivate a contact instead of deleting it
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Contact deactivated successfully."}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optionally, filter or adjust the queryset based on additional conditions, such as filtering by user
        # For example, filter contacts by the current authenticated user
        return queryset.filter(created_by=self.request.user)
