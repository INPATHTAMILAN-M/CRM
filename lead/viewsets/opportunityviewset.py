from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Opportunity, Stage
from ..serializers.opportuinityserializer import (
    OpportunitySerializer,
    PostOpportunitySerializer,
    StageUpdateSerializer,
)


class OpportunityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class ViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OpportunityPagination

    def get_queryset(self):
        user = self.request.user
        if self.action in ['retrieve', 'list']:
            if user.employee.designation.designation == 'ADMIN':
                return Opportunity.objects.filter(is_active=True)
            return Opportunity.objects.filter(
                Q(created_by=user) | Q(owner=user) |
                Q(lead__lead_owner=user) | Q(lead__created_by=user)
            ).distinct().order_by('-created_on', '-id')
        return super().get_queryset()

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
            created_by = request.user
            
            # Handle stage creation/update
            stage_data = {
                'opportunity': opportunity.id,
                'stage': data.get('stage'),
                'moved_by': created_by.id,
            }
            stage_serializer = StageUpdateSerializer(data=stage_data)
            if stage_serializer.is_valid():
                stage_serializer.save()
            else:
                return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Send email to lead owner
            lead = opportunity.lead
            lead_owner = lead.lead_owner
            subject_lead_owner = "Opportunity Linked to Your Lead"
            message_lead_owner = (
                f"Hello {lead_owner.username},\n\n"
                f"The opportunity '{opportunity.name}' has been linked to your lead '{lead.name}'.\n"
                "Please log in to the CRM system to view more details:\n"
                "http://crm.decodeschool.com/\n\n"
            )
            try:
                send_mail(
                    subject_lead_owner,
                    message_lead_owner,
                    settings.DEFAULT_FROM_EMAIL,
                    [lead_owner.email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({"message": "Opportunity created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            opportunity = Opportunity.objects.get(id=pk)
            old_stage = opportunity.stage.id if opportunity.stage else None

            data = request.data.copy()
            data.update(request.FILES)
            serializer = PostOpportunitySerializer(opportunity, data=data, partial=True)
            if serializer.is_valid():
                updated_opportunity = serializer.save()
                
                # Check if the stage changed
                new_stage = updated_opportunity.stage.id if updated_opportunity.stage else None
                if old_stage != new_stage:
                    stage = Stage.objects.get(id=new_stage)
                    updated_opportunity.probability_in_percentage = stage.probability
                    updated_opportunity.save()

                    stage_data = {
                        'opportunity': updated_opportunity.id,
                        'stage': new_stage,
                        'moved_by': request.user.id,
                    }
                    stage_serializer = StageUpdateSerializer(data=stage_data)
                    if stage_serializer.is_valid():
                        stage_serializer.save()
                    else:
                        return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['get'], url_path='active')
    def list_active(self, request):
        """
        Custom endpoint to list only active opportunities.
        """
        active_opportunities = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(active_opportunities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_opportunities, many=True)
        return Response(serializer.data)
