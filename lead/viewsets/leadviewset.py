from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Min, Max


from ..custompagination import Paginator
from ..models import Lead, Contact, Notification
from ..serializers.leadserializer import (
    LeadSerializer,
    PostLeadSerializer

)


class ViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LeadSerializer
    pagination_class = Paginator

    def get_serializer_class(self):
        # Return the correct serializer based on the action
        if self.action in ['create', 'update']:
            return PostLeadSerializer
        return LeadSerializer

    def get_queryset(self):
        user = self.request.user
        # Filter leads based on the user's group
        if user.groups.filter(name='Admin').exists():
            return Lead.objects.filter(is_active=True).order_by('-id')

        elif user.groups.filter(name='DM').exists():
            return Lead.objects.filter(created_by=user, is_active=True).order_by('-id')

        elif user.groups.filter(name='TM').exists() or user.groups.filter(name='BDE').exists():
            return Lead.objects.filter(lead_assignment__assigned_to=user, is_active=True).distinct().order_by('-id')

        elif user.groups.filter(name='BDM').exists():
            return Lead.objects.filter(lead_owner=user, is_active=True).order_by('-id')

        else:
            return Lead.objects.none()

    def perform_create(self, serializer):
        # Save the lead and assign the current logged-in user as 'created_by'
        lead = serializer.save(created_by=self.request.user)

        # Ensure that the lead_owner is valid
        try:
            lead_owner = lead.lead_owner
            if not lead_owner:
                raise ValueError("Lead owner is not set.")
            recipient_email = lead_owner.email
        except (User.DoesNotExist, ValueError) as e:
            raise Response({"error": f"Notification email not set for user: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Contact instance
        contact_data = {
            "lead": lead,
            "name": lead.name,
            "email_id": lead.company_email,
            "phone_number": lead.company_number,
            "created_by": self.request.user,
            "is_active": True,
            "is_primary": True,
        }
        Contact.objects.create(**contact_data)

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

    def perform_update(self, serializer):
        lead = serializer.save()
        # Notify the lead owner and creator about the update
        if self.request.user != lead.lead_owner:
            message = f"The lead '{lead.name}' has been updated by '{self.request.user}'."
            Notification.objects.create(receiver=lead.lead_owner, message=message)
        if self.request.user != lead.created_by:
            message = f"The lead '{lead.name}' has been updated by '{self.request.user}'."
            Notification.objects.create(receiver=lead.created_by, message=message)

    def perform_destroy(self, instance):
        # Soft-delete the lead (mark as inactive)
        instance.is_active = False
        instance.save()

        # Send notifications to the lead owner and creator about the deactivation
        if self.request.user != instance.lead_owner:
            message = f"The lead '{instance.name}' has been deactivated."
            Notification.objects.create(receiver=instance.lead_owner, message=message)
        if self.request.user != instance.created_by:
            message = f"The lead '{instance.name}' has been deactivated."
            Notification.objects.create(receiver=instance.created_by, message=message)

    def list(self, request, *args, **kwargs):
        # Custom list to return leads with min and max revenue
        queryset = self.filter_queryset(self.get_queryset())
        
        # Aggregate min and max revenue
        min_revenue = queryset.aggregate(min_revenue=Min('annual_revenue'))['min_revenue']
        max_revenue = queryset.aggregate(max_revenue=Max('annual_revenue'))['max_revenue']

        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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
        lead = self.get_object()
        opportunities = lead.opportunity_set.all()
        contacts = lead.contact_set.all()

        opportunity_data = []
        for opportunity in opportunities:
            opportunity_data.append({
                "name": opportunity.name,
                "stage": opportunity.stage.name,
                "opportunity_value": opportunity.opportunity_value,
                "created_on": opportunity.created_on,
            })

        contact_data = []
        for contact in contacts:
            contact_data.append({
                "name": contact.name,
                "email": contact.email_id,
                "phone": contact.phone_number,
                "is_primary": contact.is_primary,
            })

        return Response({
            "opportunities": opportunity_data,
            "contacts": contact_data,
        })
