from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Min, Max
from django_filters.rest_framework import DjangoFilterBackend

from ..custompagination import Paginator
from ..models import Lead, Contact, Lead_Assignment, Notification
from ..filters.lead_filter import LeadFilter
from ..serializers.lead_serializer import (
    LeadSerializer,
    PostLeadSerializer
)

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeadFilter
    serializer_class = LeadSerializer
    pagination_class = Paginator
    
    def perform_create(self, serializer):
        # Save the lead and assign the current logged-in user as 'created_by'
        lead = serializer.save(created_by=self.request.user)
        
                # Get the contact_id from the request data (if provided)
        contact_id = self.request.data.get('contact_id', None)

        # If contact_id is provided, link the contact to the created lead
        if contact_id:
            try:
                # Contact.objects.filter(lead=lead).update(is_primary=False)
                contact = Contact.objects.get(id=contact_id)
                contact.lead = lead 
                contact.is_primary= True
                contact.save()
            except Contact.DoesNotExist:
                raise Response({"error": "Contact with the provided ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lead_owner = lead.lead_owner
            if not lead_owner:
                raise ValueError("Lead owner is not set.")
            recipient_email = lead_owner.email
        except (User.DoesNotExist, ValueError) as e:
            raise Response({"error": f"Notification email not set for user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if lead.assigned_to :
            lead_assignment = {
                "lead":lead,
                "assigned_to": lead.assigned_to,
                "assigned_on": lead.assigned_on,
                "assigned_by": self.request.user,
                "is_active": True,
            }
            Lead_Assignment.objects.create(**lead_assignment)
            
        # Send an email notification to the lead owner
        subject = "New Lead Created"
        message = f"A new lead has been created by {self.request.user.username}.\n\nPlease log in to the CRM system to view more details and take further action:\nhttp://crm.decodeschool.com/"

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
        except Exception as e:
            raise Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_serializer_class(self):
        # Return the appropriate serializer based on the action (create or update)
        if self.action in ['create', 'update']:
            return PostLeadSerializer
        return LeadSerializer

    def get_queryset(self):
        user = self.request.user
        # Filter leads based on user group
        if user.groups.filter(name='Admin').exists():
            return Lead.objects.all().order_by('-id')
        elif user.groups.filter(name='DM').exists():
            return Lead.objects.filter(created_by=user, is_active=True).order_by('-id')
        elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
            return Lead.objects.filter(lead_assignment__assigned_to=user, is_active=True).distinct().order_by('-id')
        elif user.groups.filter(name='BDM').exists():
            return Lead.objects.filter(lead_owner=user, is_active=True).order_by('-id')
        else:
            return Lead.objects.none()

    def retrieve(self, request, *args, **kwargs):
        lead = Lead.objects.filter(id=kwargs['pk']).first()
        if lead:
            serializer = self.get_serializer(lead)
            return Response(serializer.data)
        else:
            return Response({"detail": "No Lead matches the given query."}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        lead = self.get_object()  # Get the lead by pk
        # Handle the case if lead doesn't exist
        if not lead:
            return Response({"error": "Lead not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the lead object
        serializer =PostLeadSerializer(lead, data=request.data, partial=True)
        if serializer.is_valid():
            lead = serializer.save()

            # Notify about the update to lead owner and creator if necessary
            if lead.lead_owner and self.request.user != lead.lead_owner:
                Notification.objects.create(receiver=lead.lead_owner, message=f"Lead '{lead.name}' has been updated by {self.request.user}.")

            if lead.created_by and self.request.user != lead.created_by:
                Notification.objects.create(receiver=lead.created_by, message=f"Lead '{lead.name}' has been updated by {self.request.user}.")

            # Handle primary contact updates
            primary_contact_data = request.data.get('primary_contact', None)
            if primary_contact_data:
                primary_contact_id = primary_contact_data.get('id')
                if primary_contact_id:
                    try:
                        primary_contact = Contact.objects.get(id=primary_contact_id, lead=lead)
                        for field, value in primary_contact_data.items():
                            setattr(primary_contact, field, value)
                            primary_contact.is_primary=True
                        primary_contact.save()
                        Contact.objects.filter(lead=lead).exclude(id=primary_contact_id).update(is_primary=False)
                    except Contact.DoesNotExist:
                        return Response({"error": "Primary contact not found or doesn't belong to this lead."}, status=status.HTTP_404_NOT_FOUND)
                else: 
                    return Response({"error": "Primary contact ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": "Lead updated successfully.",}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        # Soft-delete the lead (mark as inactive)
        instance.is_active = False
        instance.save()

        # Send notifications to the lead owner and creator about the deactivation
        if self.request.user != instance.lead_owner:
            Notification.objects.create(receiver=instance.lead_owner, message=f"Lead '{instance.name}' has been deactivated.")
        if self.request.user != instance.created_by:
            Notification.objects.create(receiver=instance.created_by, message=f"Lead '{instance.name}' has been deactivated.")

    def list(self, request, *args, **kwargs):
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Aggregate min and max revenue
        min_revenue = queryset.aggregate(min_revenue=Min('annual_revenue'))['min_revenue']
        max_revenue = queryset.aggregate(max_revenue=Max('annual_revenue'))['max_revenue']

        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Return unpaginated response with revenue data
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        response_data.append({
            "min_revenue": min_revenue,
            "max_revenue": max_revenue,
        })
        return Response(response_data)

    @action(detail=True, methods=['get'])
    def opportunities(self, request, pk=None):
        """
        Custom action to get opportunities and contacts for a specific lead.
        """
        lead = self.get_object()  # Get the lead by pk
        opportunities = lead.opportunity_set.all()
        contacts = lead.contact_set.all()

        # Prepare the opportunity data
        opportunity_data = [{
            "name": opportunity.name,
            "stage": opportunity.stage.name,
            "opportunity_value": opportunity.opportunity_value,
            "created_on": opportunity.created_on,
        } for opportunity in opportunities]

        # Prepare the contact data
        contact_data = [{
            "name": contact.name,
            "email": contact.email_id,
            "phone": contact.phone_number,
            "is_primary": contact.is_primary,
        } for contact in contacts]

        return Response({
            "opportunities": opportunity_data,
            "contacts": contact_data,
        })

