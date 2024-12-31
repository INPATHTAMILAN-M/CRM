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
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads

    def post(self, request, *args, **kwargs):
        """
        Import contacts from an Excel file.
        """
        # Get the uploaded file from the request
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Load the workbook and get the active sheet
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            # List to hold the contact data to be created
            contacts_data = []

            # Iterate over the rows in the Excel sheet starting from row 2 (skip header row)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                contact_data = {
                    'lead': row[0] if row[0] else None,
                    'name': row[1] if row[1] else '',  
                    'status': row[2] if row[2] else None,  
                    'designation': row[3] if row[3] else '', 
                    'department': row[4] if row[4] else '',  
                    'phone_number': row[5] if row[5] else '',  
                    'email_id': row[6] if row[6] else None, 
                    'remark': row[7] if row[7] else '',  
                    'lead_source': row[8] if row[8] else None, 
                    'is_active': row[9] == 'TRUE',  
                    'is_archive': row[10] == 'TRUE',  
                    'created_by': request.user.id,  
                }
                contacts_data.append(contact_data)

            # Now, serialize the contact data
            serializer = ContactCreateSerializer(data=contacts_data, many=True)

            # Check if the data is valid and save it
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Contacts imported successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Failed to process the Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
