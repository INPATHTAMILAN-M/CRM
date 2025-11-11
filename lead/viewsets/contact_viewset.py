from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models.functions import Greatest
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
    queryset = (
        Contact.objects.filter(is_active=True)
        .annotate(latest_activity=Greatest('created_on', 'updated_on'))
        .order_by('-latest_activity')
    )
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

                # # Extract row data into a dictionary
                # contact_data = {
                #     'lead': row.get('lead') if pd.notnull(row.get('lead')) else None,
                #     'name': row.get('name') if pd.notnull(row.get('name')) else None,
                #     'company_name': row.get('company_name') if pd.notnull(row.get('company_name')) else None,
                #     'status': row.get('status') if pd.notnull(row.get('status')) else None,
                #     'designation': row.get('designation') if pd.notnull(row.get('designation')) else None,
                #     'department': row.get('department') if pd.notnull(row.get('department')) else None,
                #     'phone_number': row.get('phone_number') if pd.notnull(row.get('phone_number')) else None,
                #     'secondary_phone_number': row.get('secondary_phone_number') if pd.notnull(row.get('secondary_phone_number')) else None,
                #     'email_id': row.get('email_id') if pd.notnull(row.get('email_id')) else None,
                #     'remark': row.get('remark') if pd.notnull(row.get('remark')) else None,
                #     'lead_source': row.get('lead_source') if pd.notnull(row.get('lead_source')) else None,
                #     'lead_source_from': row.get('lead_source_from') if pd.notnull(row.get('lead_source_from')) else None,
                #     'is_active': row.get('is_active') == 'TRUE' if pd.notnull(row.get('is_active')) else True,
                #     'is_archive': row.get('is_archive') == 'TRUE' if pd.notnull(row.get('is_archive')) else False,
                #     'created_by': request.user.id,
                # }
                def clean(value):
                    return str(value).strip() if pd.notnull(value) else None

                contact_data = {
                    'lead': clean(row.get('lead')),
                    'name': clean(row.get('name')),
                    'company_name': clean(row.get('company_name')),
                    'status': clean(row.get('status')),
                    'designation': clean(row.get('designation')),
                    'department': clean(row.get('department')),
                    'phone_number': clean(row.get('phone_number')),
                    'secondary_phone_number': clean(row.get('secondary_phone_number')),
                    'email_id': clean(row.get('email_id')),
                    'remark': clean(row.get('remark')),
                    'lead_source': clean(row.get('lead_source')),
                    'lead_source_from': clean(row.get('lead_source_from')),
                    'is_active': str(row.get('is_active')).strip().lower() == 'true' if pd.notnull(row.get('is_active')) else True,
                    'is_archive': str(row.get('is_archive')).strip().lower() == 'true' if pd.notnull(row.get('is_archive')) else False,
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


# views.py
import pandas as pd
from datetime import datetime
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from lead.serializers.contact_import_serializer import BulkImportSerializer
from accounts.models import User
from lead.models import (
    Lead, Contact, Lead_Status, Opportunity, Opportunity_Name,
    Stage, Lead_Bucket, Country, Log, Log_Stage
)



class BulkImportAPIView(APIView):
    """
    Imports data from an Excel file and creates Lead, Contact, Opportunity, and Log entries.
    Accepts a file via POST or uses a given path during dev.
    """

    def parse_excel_date(self, value):
        """Parses Excel date strings like '03/10/2025' or 'DD/MM/YYYY' safely."""
        if not value or pd.isna(value):
            return datetime.today().date()
        try:
            # Explicitly specify DD/MM/YYYY format to avoid ambiguity
            parsed = pd.to_datetime(value, format='%d/%m/%Y', errors='coerce')
            if pd.isna(parsed):
                return datetime.today().date()
            return parsed.date()
        except Exception:
            return datetime.today().date()
    
    def clean_float(self, value):
        """Safely convert value to float, handling NaN and None."""
        if value is None or pd.isna(value):
            return 0
        try:
            float_val = float(value)
            # Check if it's a valid finite number
            if not pd.isna(float_val) and float_val != float('inf') and float_val != float('-inf'):
                return float_val
            return 0
        except (ValueError, TypeError):
            return 0
    
    def clean_string(self, value):
        """Safely convert value to string, handling NaN and None."""
        if value is None or pd.isna(value):
            return None
        return str(value).strip() if str(value).strip() else None

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        df.columns = df.columns.str.strip().str.lower()
        df = df.where(pd.notnull(df), None)
        data = df.to_dict(orient="records")

        # ---- Default fallbacks ----
        default_user = User.objects.filter(is_superuser=True).first()
        default_stage = Stage.objects.first()
        default_status = Lead_Status.objects.first()
        default_bucket = Lead_Bucket.objects.first()
        default_country = Country.objects.first()
        default_opportunity_name = Opportunity_Name.objects.first()
        default_log_stage = Log_Stage.objects.first()

        created_records = {
            "leads": 0,
            "contacts": 0,
            "opportunities": 0,
            "logs": 0,
        }
        
        errors = []

        for index, row in enumerate(data, start=1):
            try:
                # ---- Parse dates safely ----
                created_date = self.parse_excel_date(row.get("date"))
                closing_date = self.parse_excel_date(row.get("date")) 

                # ---- Clean string values ----
                company_name = self.clean_string(row.get("company_name")) or f"Lead_{index}"
                contact_name = self.clean_string(row.get("name"))
                phone_number = self.clean_string(row.get("phone_number"))
                remark = self.clean_string(row.get("remark"))
                designation = self.clean_string(row.get("designation"))
                
                # ---- Clean float values ----
                opportunity_value = self.clean_float(row.get("opportunity_value"))
                recurring_value = self.clean_float(row.get("recurring_value_per_year"))
                probability = self.clean_float(row.get("probability_in_percentage"))

                # ---- Identify user ----
                created_by_user = User.objects.filter(username=designation).first() or default_user

                # ---- LEAD ----
                lead = Lead.objects.create(
                    name=company_name,
                    lead_status=default_status,
                    lead_owner=created_by_user,
                    created_by=created_by_user,
                    remark=remark,
                    lead_type="Manual Lead",
                    is_active=True,
                )
                Lead.objects.filter(pk=lead.pk).update(created_on=created_date)
                lead.refresh_from_db()
                created_records["leads"] += 1

                # ---- CONTACT ----
                contact = Contact.objects.create(
                    lead=lead,
                    company_name=company_name,
                    name=contact_name,
                    phone_number=phone_number,
                    remark=remark,
                    created_by=created_by_user,
                    is_primary=True,
                    is_active=True,
                )
                Contact.objects.filter(pk=contact.pk).update(created_on=created_date)
                contact.refresh_from_db()
                created_records["contacts"] += 1

                # ---- OPPORTUNITY ----
                opportunity = Opportunity.objects.create(
                    lead=lead,
                    primary_contact=contact,
                    name=default_opportunity_name,
                    stage=default_stage,
                    owner=created_by_user,
                    note=remark,
                    opportunity_value=opportunity_value,
                    recurring_value_per_year=recurring_value,
                    currency_type=default_country,
                    closing_date=closing_date,
                    probability_in_percentage=probability,
                    lead_bucket=default_bucket,
                    created_by=created_by_user,
                    opportunity_status=default_status,
                    status_date=created_date,
                    remark=remark,
                    is_active=True,
                )
                Opportunity.objects.filter(pk=opportunity.pk).update(created_on=created_date)
                opportunity.refresh_from_db()
                created_records["opportunities"] += 1

                # ---- LOG ----
                Log.objects.create(
                    lead=lead,
                    created_by=created_by_user,
                    contact_id=contact.id,
                    details=remark or f"Imported lead {lead.name}",
                    log_type="Call",
                    log_stage=default_log_stage,
                    focus_segment=getattr(lead, "focus_segment", None),
                    created_on=created_date,
                )
                created_records["logs"] += 1

            except Exception as e:
                errors.append({
                    "row": index,
                    "error": str(e)
                })

        response_data = {
            "message": "Import completed successfully." if not errors else "Import completed with errors.",
            "summary": created_records,
        }
        
        if errors:
            response_data["errors"] = errors
            response_data["total_errors"] = len(errors)
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS,
        )

