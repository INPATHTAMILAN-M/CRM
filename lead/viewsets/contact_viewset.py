from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from lead.custompagination import Paginator
from ..models import Contact
from ..serializers.contact_serializer import *
from ..paginations.contact_pagination import ContactPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.contact_filter import ContactFilter

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()  
    permission_classes = [IsAuthenticated]  
    pagination_class = Paginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContactFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactCreateSerializer
        if self.action == 'list':
            return ContactListSerializer
        if self.action in ['update', 'partial_update']:
            return ContactUpdateSerializer
        return ContactDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Contact deactivated successfully."}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
