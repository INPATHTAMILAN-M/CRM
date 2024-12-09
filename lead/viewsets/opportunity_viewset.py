from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Opportunity, Stage
from ..custompagination import Paginator
from ..serializers.opportuinityserializer import (
    OpportunitySerializer,
    PostOpportunitySerializer,
    StageUpdateSerializer,
)


class ViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator

    def get_queryset(self):
        user = self.request.user
        if user.employee.designation.designation == 'ADMIN':
            return Opportunity.objects.filter(is_active=True)
        return Opportunity.objects.filter(
            Q(created_by=user) | Q(owner=user) | 
            Q(lead__lead_owner=user) | Q(lead__created_by=user)
        ).distinct().order_by('-created_on', '-id')

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            opportunity = Opportunity.objects.get(id=pk)
            serializer = self.get_serializer(opportunity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Opportunity.DoesNotExist:
            return Response({"detail": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update(request.FILES)
        serializer = PostOpportunitySerializer(data=data)

        if serializer.is_valid():
            opportunity = serializer.save(created_by=request.user)
            # self.handle_stage_update(opportunity, data)
            self.send_lead_owner_email(opportunity)
            return Response({"message": "Opportunity created", "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        try:
            opportunity = Opportunity.objects.get(id=pk)
            data = request.data.copy()
            data.update(request.FILES)
            serializer = PostOpportunitySerializer(opportunity, data=data, partial=True)

            if serializer.is_valid():
                updated_opportunity = serializer.save()
                # self.handle_stage_update(updated_opportunity, data)
                return Response({"message": "Opportunity updated", "data": self.get_serializer(updated_opportunity).data}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            opportunity = Opportunity.objects.get(id=pk)
            opportunity.is_active = False
            opportunity.save()
            return Response({"message": "Opportunity deactivated"}, status=status.HTTP_204_NO_CONTENT)
        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)

    def handle_stage_update(self, opportunity, data):
        """Handle stage creation or update."""
        old_stage = opportunity.stage.id if opportunity.stage else None
        new_stage = data.get('stage')

        if old_stage != new_stage:
            stage = Stage.objects.get(id=new_stage)
            opportunity.probability_in_percentage = stage.probability
            opportunity.save()

            stage_data = {
                'opportunity': opportunity.id,
                'stage': new_stage,
                'moved_by': self.request.user.id,
            }
            stage_serializer = StageUpdateSerializer(data=stage_data)
            if stage_serializer.is_valid():
                stage_serializer.save()

    def send_lead_owner_email(self, opportunity):
        """Send an email notification to the lead owner."""
        try:
            lead_owner = opportunity.lead.lead_owner
            subject = "Opportunity Linked to Your Lead"
            message = (
                f"Hello {lead_owner.username},\n\n"
                f"The opportunity '{opportunity.name}' has been linked to your lead '{opportunity.lead.name}'.\n"
                "Please log in to the CRM system to view more details:\n"
                "http://crm.decodeschool.com/\n\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [lead_owner.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log email error if necessary
            pass
