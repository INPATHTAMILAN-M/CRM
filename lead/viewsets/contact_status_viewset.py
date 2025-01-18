from rest_framework import filters
from django_filters import rest_framework as django_filters
from rest_framework import viewsets
from rest_framework.response import Response
from accounts.models import Contact_Status
from lead.custompagination import Paginator
from lead.filters.contact_status_filter import ContactStatusFilter
from lead.serializers.contact_status_serializer import ContactStatusSerializer
from rest_framework import status

class ContactStatusViewSet(viewsets.ModelViewSet):
    queryset = Contact_Status.objects.all().order_by('-id')
    serializer_class = ContactStatusSerializer
    filter_backends = (filters.OrderingFilter, django_filters.DjangoFilterBackend)
    filterset_class = ContactStatusFilter
    ordering_fields = '__all__'
    ordering = ['status']
    pagination_class = Paginator
    

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get('is_active')
        instance.is_active = is_active
        instance.save()

        if is_active == 'True':
            return Response(
                {"detail": "Activated Successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Deactivated Successfully."},
                status=status.HTTP_200_OK
            )