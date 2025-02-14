from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from lead.custom_pagination import Paginator
from ..models import Lead_Status
from ..serializers.lead_status_serializer import LeadStatusSerializer
from ..filters.lead_status_filter import LeadStatusFilter
from rest_framework import status
from rest_framework.response import Response

class LeadStatusViewSet(viewsets.ModelViewSet):
    queryset = Lead_Status.objects.all().order_by('-id')
    serializer_class = LeadStatusSerializer
    filter_backends = (DjangoFilterBackend,)  # Specify the filter backend
    filterset_class = LeadStatusFilter  # Use the filter class here
    pagination_class = Paginator
    
    def get_queryset(self):
        # Get the user group
        user_groups = self.request.user.groups.values_list('name', flat=True)
        
        # Check if the user belongs to the 'DM' group
        if 'DM' in user_groups:
            # If the user is in the 'DM' group, show all lead statuses
            return Lead_Status.objects.all()
        else:
            # If not, exclude "InProgress Lead" and "Fresh Lead" lead statuses
            return Lead_Status.objects.exclude(name__in=["InProgress Lead", "Fresh Lead"])

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