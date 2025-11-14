from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q, Case, When, F
from django.db.models.functions import Greatest,Coalesce
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Opportunity, Stage
from ..custom_pagination import Paginator
from ..serializers.opportuinity_serializer import (
    OpportunityDetailSerializer,
    OpportunityCreateSerializer,
    OpportunityListSerializer,
    OpportunityUpdateSerializer,
    StageUpdateSerializer,
)
from ..models import Opportunity
from rest_framework import serializers

from ..filters.opportunity_filter import OpportunityFilter


class OpportunityViewset(viewsets.ModelViewSet):
    queryset = Opportunity.objects.select_related(
        'lead', 'owner', 'created_by', 'stage', 'primary_contact', 'currency_type', 'opportunity_status'
    ).prefetch_related('log_set').order_by('-created_on')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OpportunityFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True)
        
        if self.request.query_params.get('display_date_source'):
            queryset = queryset.annotate(
                latest_activity=Greatest(
                    Coalesce('updated_on', 'created_on'),
                    Coalesce('created_on', 'updated_on')
                )
            ).order_by('-latest_activity')
        else:
            queryset = queryset.order_by('-created_on')
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return OpportunityCreateSerializer
        if self.action == 'list':
            return OpportunityListSerializer
        if self.action in ['update', 'partial_update']:
            return OpportunityUpdateSerializer
        return OpportunityDetailSerializer
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    def perform_create(self, serializer):
        self.send_lead_owner_email(serializer.instance)
        serializer.save(created_by=self.request.user)
        
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
            # Get the new stage object
            stage = Stage.objects.get(id=new_stage)
            
            # Update the probability_in_percentage based on the new stage
            opportunity.probability_in_percentage = stage.probability
            opportunity.save()

            # Create a new Opportunity_Stage record to track the stage change
            opportunity_stage_data = {
                'opportunity': opportunity.id,
                'stage': new_stage,
                'moved_by': self.request.user.id,  # The user who made the change
            }
            
            # Serialize the Opportunity_Stage data and save it
            stage_serializer = StageUpdateSerializer(data=opportunity_stage_data)
            if stage_serializer.is_valid():
                stage_serializer.save()  # Create the Opportunity_Stage
            else:
                # Handle errors in the serializer if any
                raise serializers.ValidationError(stage_serializer.errors)


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
