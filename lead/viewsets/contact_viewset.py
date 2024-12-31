from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import openpyxl

from lead.custompagination import Paginator
from ..models import Contact
from ..serializers.contact_serializer import *
from ..paginations.contact_pagination import ContactPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.contact_filter import ContactFilter

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()  
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
        return Response({"message": "Contact deactivated successfully."}, status=status.HTTP_200_OK)

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(created_by=self.request.user)

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

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row):  
                    continue

                name = row[column_mapping.get('name')] if column_mapping.get('name') is not None else None
                lead = row[column_mapping.get('lead')] if column_mapping.get('lead') is not None else None
                contact_status = row[column_mapping.get('status')] if column_mapping.get('status') is not None else None
                designation = row[column_mapping.get('designation')] if column_mapping.get('designation') is not None else None
                department = row[column_mapping.get('department')] if column_mapping.get('department') is not None else None
                phone_number = row[column_mapping.get('phone_number')] if column_mapping.get('phone_number') is not None else None
                email_id = row[column_mapping.get('email_id')] if column_mapping.get('email_id') is not None else None
                remark = row[column_mapping.get('remark')] if column_mapping.get('remark') is not None else None
                lead_source = row[column_mapping.get('lead_source')] if column_mapping.get('lead_source') is not None else None
                is_active = row[column_mapping.get('is_active')] == 'TRUE' if column_mapping.get('is_active') is not None else False
                is_archive = row[column_mapping.get('is_archive')] == 'TRUE' if column_mapping.get('is_archive') is not None else False

                if not name :
                    print("Skipping row due to missing required fields: ", row)
                    continue  

                contact_data = {
                    'lead': lead,
                    'name': name,
                    'status': contact_status,
                    'designation': designation,
                    'department': department,
                    'phone_number': phone_number,
                    'email_id': email_id,
                    'remark': remark,
                    'lead_source': lead_source,
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
                return Response({"message": "Contacts imported successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            return Response({"error": "Invalid data", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to process the Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)