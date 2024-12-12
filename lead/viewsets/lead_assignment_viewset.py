from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from lead.filters.lead_assignment_filter import LeadAssignmentFilter
from ..models import Lead_Assignment
from ..serializers.lead_assignment_serializer import LeadAssignmentSerializer
from rest_framework.permissions import IsAuthenticated

class LeadAssignmentViewSet(viewsets.ModelViewSet):
    queryset = Lead_Assignment.objects.all()
    serializer_class = LeadAssignmentSerializer
    permission_classes = [IsAuthenticated]  # Optional: Ensure that the user is authenticated
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeadAssignmentFilter
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )