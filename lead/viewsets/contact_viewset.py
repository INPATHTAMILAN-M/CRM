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
    queryset = Contact.objects.all().order_by('-id')
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
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "deactivated successfully."}, status=status.HTTP_200_OK)

class ImportContactsAPIView(APIView): 
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            headers = [cell.value.strip() if cell.value else "" for cell in sheet[1]]
            headers = [header for header in headers if header]

            if len(headers) == 0:
                return Response({"error": "Excel contains no valid header fields."}, status=status.HTTP_400_BAD_REQUEST)

            column_mapping = {}
            for index, header in enumerate(headers):
                column_mapping[header.lower()] = index

            contacts_data = []
            errored_contacts = []  # To store contacts with errors for response

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row):  
                    continue

                name = row[column_mapping.get('name')] if column_mapping.get('name') is not None else None
                lead = row[column_mapping.get('lead')] if column_mapping.get('lead') is not None else None
                company_name = row[column_mapping.get('company_name')] if column_mapping.get('company_name') is not None else None
                contact_status_name = row[column_mapping.get('status')] if column_mapping.get('status') is not None else None
                designation = row[column_mapping.get('designation')] if column_mapping.get('designation') is not None else None
                department_name = row[column_mapping.get('department')] if column_mapping.get('department') is not None else None
                phone_number = row[column_mapping.get('phone_number')] if column_mapping.get('phone_number') is not None else None
                email_id = row[column_mapping.get('email_id')] if column_mapping.get('email_id') is not None else None
                remark = row[column_mapping.get('remark')] if column_mapping.get('remark') is not None else None
                lead_source_name = row[column_mapping.get('lead_source')] if column_mapping.get('lead_source') is not None else None
                lead_source_from_name = row[column_mapping.get('lead_source_from')] if column_mapping.get('lead_source_from') is not None else None
                is_active = row[column_mapping.get('is_active')] == 'TRUE' if column_mapping.get('is_active') is not None else False
                is_archive = row[column_mapping.get('is_archive')] == 'TRUE' if column_mapping.get('is_archive') is not None else False
                
                if not name:
                    errored_contacts.append({'company_name': company_name, 'error': 'Missing name'})
                    continue

                # Querying database for the IDs based on name
                contact_status = None
                if contact_status_name:
                    try:
                        contact_status = Contact_Status.objects.get(status=contact_status_name, is_active=True)
                    except ObjectDoesNotExist:
                        errored_contacts.append({'company_name': company_name, 'error': f"Contact status '{contact_status_name}' not found"})
                        continue

                department = None
                if department_name:
                    try:
                        department = Department.objects.get(department=department_name, is_active=True)
                    except ObjectDoesNotExist:
                        errored_contacts.append({'company_name': company_name, 'error': f"Department '{department_name}' not found"})
                        continue

                lead_source = None
                if lead_source_name:
                    try:
                        lead_source = Lead_Source.objects.get(source=lead_source_name, is_active=True)
                    except ObjectDoesNotExist:
                        errored_contacts.append({'company_name': company_name, 'error': f"Lead source '{lead_source_name}' not found"})
                        continue

                lead_source_from = None
                if lead_source_from_name:
                    try:
                        lead_source_from = Lead_Source_From.objects.get(source_from=lead_source_from_name, is_active=True)
                    except ObjectDoesNotExist:
                        errored_contacts.append({'company_name': company_name, 'error': f"Lead source from '{lead_source_from_name}' not found"})
                        continue

                # Check for duplicate company_name or phone_number
                if Contact.objects.filter(company_name=company_name).exists():
                    errored_contacts.append({'company_name': company_name, 'error': 'Contact with this company name already exists'})
                    continue

                if Contact.objects.filter(phone_number=phone_number).exists():
                    errored_contacts.append({'company_name': company_name, 'error': 'Contact with this phone number already exists'})
                    continue

                contact_data = {
                    'lead': lead,
                    'name': name,
                    'company_name': company_name,
                    'contact_status': contact_status.id if contact_status else None,
                    'designation': designation,
                    'department': department.id if department else None,
                    'phone_number': phone_number,
                    'email_id': email_id,
                    'remark': remark,
                    'lead_source': lead_source.id if lead_source else None,
                    'lead_source_from': lead_source_from.id if lead_source_from else None,
                    'is_active': is_active,
                    'is_archive': is_archive,
                    'created_by': request.user.id,
                }
                contacts_data.append(contact_data)

            if not contacts_data:
                return Response({"error": "No valid contacts found in the file."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ContactImportCreateSerializer(data=contacts_data, many=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {"message": "Contacts imported successfully", "data": serializer.data}
                if errored_contacts:
                    response_data["errored_contacts"] = errored_contacts
                return Response(response_data, status=status.HTTP_201_CREATED)

            # Return the error details including the `id` and `company_name` for errored rows
            error_details = []
            for contact, error in zip(contacts_data, serializer.errors):
                contact_error = {
                    "id": contact.get("id", "N/A"),
                    "company_name": contact.get("company_name", "N/A"),
                    "error": error
                }
                error_details.append(contact_error)

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
import pandas as pd
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class ImportLeadsAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Read the Excel file
        try:
            df = pd.read_excel(file, keep_default_na=False, sheet_name='Ramu 18.02.25')
        except Exception as e:
            return Response({'error': f'Error reading Excel file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        errors = []

        # Start atomic transaction
        with transaction.atomic():
            for index, row in df.iterrows():
                from pprint import pprint
                serializer = LeadImportSerializer(data=row.to_dict())

                if serializer.is_valid():
                    validated_data = serializer.validated_data

                    # Use request.user if lead_owner is not in validated_data
                    lead_owner = validated_data.get('lead_owner', request.user)

                    # Check if Lead exists, else create
                    lead, created_lead = Lead.objects.get_or_create(
                        name=validated_data['company_name'],
                        defaults={
                            'lead_owner': lead_owner,
                            'created_by': User.objects.get(id=11),
                            'address': validated_data.get('address'),
                            'country': validated_data.get('country'),
                            'state': validated_data.get('state'),
                            'city': validated_data.get('city'),
                            'assigned_to': None,
                        }
                    )

                    # Create or get Contact
                    contact, created_contact = Contact.objects.get_or_create(
                        phone_number=validated_data.get('phone_number'),
                        defaults={
                            'lead': lead,
                            'name': validated_data['name'],
                            'created_by': User.objects.get(id=11),
                            'remark': validated_data.get('remark'),
                            'status': validated_data.get('status'),
                        }
                    )


                    print("Existing Contact:", contact if not created_contact else None)
                    print("Newly Created Contact:", contact if created_contact else None)

                    Opportunity.objects.create(
                        lead=lead,
                        name=validated_data.get('opportunity_name'),
                        created_by=User.objects.get(id=11),
                        opportunity_value=0,
                        closing_date=datetime.today() + timedelta(days=30),
                        probability_in_percentage=0,
                        opportunity_status = validated_data.get('opportunity_status'),
                        status_date = validated_data.get('status_date') or datetime.today(),               
                        )

                else:
                    # Collect row-specific errors
                    errors.append({
                        'row': index + 2,  # Excel row starts from 2 (including header)
                        'errors': serializer.errors
                    })

            # If there are errors, rollback transaction
            if errors:
                transaction.set_rollback(True)
                return Response({'status': 'error', 'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({'status': 'success', 'message': 'File processed successfully'}, status=status.HTTP_200_OK)

