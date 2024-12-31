from rest_framework import filters
from django_filters import rest_framework as django_filters
from rest_framework import viewsets

from accounts.models import Contact_Status
from lead.filters.contact_status_filter import ContactStatusFilter
from lead.serializers.contact_status_serializer import ContactStatusSerializer


class ContactStatusViewSet(viewsets.ModelViewSet):
    queryset = Contact_Status.objects.all().order_by('-id')
    serializer_class = ContactStatusSerializer
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = ContactStatusFilter
    ordering_fields = '__all__'
    ordering = ['status']  # Default ordering by 'status'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
