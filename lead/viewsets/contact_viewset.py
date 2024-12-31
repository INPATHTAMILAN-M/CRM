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
                    'lead': row[0],  # 'lead' is in the first column
                    'name': row[1],  # 'name' is in the second column
                    'status': row[2],  # 'status' is in the third column
                    'designation': row[3],  # 'designation' is in the fourth column
                    'department': row[4],  # 'department' is in the fifth column
                    'phone_number': row[5],  # 'phone_number' is in the sixth column
                    'email_id': row[6],  # 'email_id' is in the seventh column
                    'remark': row[7],  # 'remark' is in the eighth column
                    'lead_source': row[8],  # 'lead_source' is in the ninth column
                    'is_active': row[9] == 'TRUE',  # Convert 'TRUE'/'FALSE' string to Boolean
                    'is_archive': row[10] == 'TRUE',  # Convert 'TRUE'/'FALSE' string to Boolean
                    'created_by': request.user.id,  # Set logged-in user as creator
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
