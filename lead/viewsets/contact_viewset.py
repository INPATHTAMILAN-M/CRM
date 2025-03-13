from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import openpyxl
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Lead_Source_From 
from lead.custom_pagination import Paginator
from ..models import Contact, Opportunity
from ..serializers.contact_serializer import *
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.contact_filter import ContactFilter

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import pandas as pd
from ..serializers.lead_import_serializer import LeadImportSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by( '-updated_on','-created_on')
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
    
    # def get_queryset(self):
    #     user = self.request.user
    #     if user:
    #         return Contact.objects.filter(created_by=user)
    #     else:
    #         return Contact.objects.none()
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "deactivated successfully."}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from ..serializers.contact_import_serializer import ContactImportCreateSerializer


class ImportContactsAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ContactImportCreateSerializer

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Load and parse the Excel file using pandas
            df = pd.read_excel(file)

            # Check if there are any headers
            if df.empty:
                return Response({"error": "Excel contains no valid data."}, status=status.HTTP_400_BAD_REQUEST)

            # Normalize column names to lowercase and strip any extra spaces
            df.columns = df.columns.str.strip().str.lower()

            # Validate if necessary columns are present
            required_columns = ['company_name']  # You can add more required columns here
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({"error": f"Missing required columns: {', '.join(missing_columns)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Create the contact data to be serialized
            contacts_data = []
            errored_contacts = []  # To store contacts with errors for response

            for _, row in df.iterrows():
                if pd.isnull(row.get('company_name')):
                    errored_contacts.append({'company_name': None, 'error': 'Missing company_name'})
                    continue

                # Extract row data into a dictionary
                contact_data = {
                    'lead': row.get('lead') if pd.notnull(row.get('lead')) else None,
                    'name': row.get('name') if pd.notnull(row.get('name')) else None,
                    'company_name': row.get('company_name') if pd.notnull(row.get('company_name')) else None,
                    'status': row.get('status') if pd.notnull(row.get('status')) else None,
                    'designation': row.get('designation') if pd.notnull(row.get('designation')) else None,
                    'department': row.get('department') if pd.notnull(row.get('department')) else None,
                    'phone_number': row.get('phone_number') if pd.notnull(row.get('phone_number')) else None,
                    'secondary_phone_number': row.get('secondary_phone_number') if pd.notnull(row.get('secondary_phone_number')) else None,
                    'email_id': row.get('email_id') if pd.notnull(row.get('email_id')) else None,
                    'remark': row.get('remark') if pd.notnull(row.get('remark')) else None,
                    'lead_source': row.get('lead_source') if pd.notnull(row.get('lead_source')) else None,
                    'lead_source_from': row.get('lead_source_from') if pd.notnull(row.get('lead_source_from')) else None,
                    'is_active': row.get('is_active') == 'TRUE' if pd.notnull(row.get('is_active')) else False,
                    'is_archive': row.get('is_archive') == 'TRUE' if pd.notnull(row.get('is_archive')) else False,
                    'created_by': request.user.id,
                }

                contacts_data.append(contact_data)
            if not contacts_data:
                return Response({"error": "No valid contacts found in the file."}, status=status.HTTP_400_BAD_REQUEST)

            # Use serializer to validate and save contacts
            serializer = self.serializer_class(data=contacts_data, many=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {"message": "Contacts imported successfully", "data": serializer.data}
                if errored_contacts:
                    response_data["errored_contacts"] = errored_contacts
                return Response(response_data, status=status.HTTP_201_CREATED)

            # Return the error details if validation fails
            error_details = [{"company_name": contact.get("company_name", "N/A"), "error": error}
                             for contact, error in zip(contacts_data, serializer.errors)]
            return Response({"error": "Invalid data", "details": error_details}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Failed to process the Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from datetime import datetime, timedelta
from ..models import Opportunity, Opportunity_Name, Lead, Contact, User
from lead.serializers.lead_import_serializer import LeadImportSerializer
import pandas as pd
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class ImportLeadsAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read Excel file
            df = pd.read_excel(file, keep_default_na=False, sheet_name='Inbound Leads Feb 25')
        except Exception as e:
            return Response({'error': f'Error reading Excel file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        errors = []

        with transaction.atomic():
            for index, row in df.iterrows():
                serializer = LeadImportSerializer(data=row.to_dict())

                if serializer.is_valid():
                    validated_data = serializer.validated_data

                    # Determine lead owner
                    lead_owner = validated_data.get('lead_owner', request.user)

                    # Get or create Lead
                    lead, created_lead = Lead.objects.get_or_create(
                        name=validated_data['company_name'],
                        defaults={
                            'lead_owner': lead_owner,
                            'created_by': User.objects.get(id=16),
                            'address': validated_data.get('address'),
                            'country': validated_data.get('country'),
                            'state': validated_data.get('state'),
                            'city': validated_data.get('city'),
                            'remark': validated_data.get('remark'),
                            'lead_source' : validated_data.get('lead_source'),
                            'assigned_to': None,
                        }
                    )
                    contact, created_contact = Contact.objects.get_or_create(
                        phone_number=validated_data.get('phone_number'),
                        defaults={
                            'lead': lead,
                            'name': validated_data['name'],
                            'created_by': request.user,
                            'remark': validated_data.get('remark'),
                            'status': validated_data.get('status'),

                            'designation': validated_data.get('designation'),
                            'department': validated_data.get('department'),
                            'email_id': validated_data.get('email_id'),
                            'lead_source' : validated_data.get('lead_source'),
    
                            'is_active': True,
                            'is_primary': True
                        }
                    )

                    print(f"Contact {'created' if created_contact else 'exists'}: {contact}")

                    # Fetch Opportunity Name (string)
                    opportunity_obj = Opportunity_Name.objects.filter(name=validated_data.get('opportunity_name')).first()
                    opportunity = opportunity_obj if opportunity_obj else None

                    if not opportunity:
                        print(f"Opportunity Name Not Found: {validated_data.get('opportunity_name')}")
                        continue  # Skip opportunity creation if name is invalid

                    # Update or create Opportunity
                    opportunity, created_opportunity = Opportunity.objects.update_or_create(
                        lead=lead,
                        name=opportunity,
                        defaults={
                            'created_by': request.user,
                            'opportunity_value': 0,
                            'closing_date': datetime.today() + timedelta(days=30),
                            'probability_in_percentage': 0,
                            'primary_contact': contact,
                            'opportunity_status': validated_data.get('opportunity_status'),
                            'remark': validated_data.get('remark'),
                            'status_date': validated_data.get('status_date') or datetime.today(),
                        }
                    )
                    print(f"Opportunity {'created' if created_opportunity else 'updated'}: {opportunity}")

                else:
                    errors.append({
                        'row': index + 2,  # Excel row starts from 2 (including header)
                        'errors': serializer.errors
                    })

            if errors:
                transaction.set_rollback(True)
                return Response({'status': 'error', 'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({'status': 'success', 'message': 'File processed successfully'}, status=status.HTTP_200_OK)

