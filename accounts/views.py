from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate that email and password are provided
        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the password is correct
        if not user.check_password(password):
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'designation': user.userprofile.designation.designation if hasattr(user, 'userprofile') and user.userprofile.designation else None,
            # Add any other fields you need here
        }

        # Generate tokens for the authenticated user
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        }, status=status.HTTP_200_OK)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Default values in case the employee or related data is missing
        employee_data = {
            "phone_number": None,
            "designation_id": None,
            "designation": None,
            "department_id": None,
            "department": None,
            "joined_on": None,
            "gender": None,
            "blood_group": None,
            "address": None,
            "profile_photo": None,
        }

        # Check if the user has an associated employee
        try:
            employee = user.employee  # Get the related Employee object
        except employee.DoesNotExist:
            raise NotFound("User does not have associated employee data.")
        
        # Update the employee data if the Employee object exists
        employee_data.update({
            "phone_number": employee.phone_number,
            "designation_id": employee.designation.id if employee.designation else None,
            "designation": employee.designation.designation if employee.designation else None,
            "department_id": employee.department.id if employee.department else None,
            "department": employee.department.department if employee.department else None,
            "joined_on": employee.joined_on,
            "gender": employee.gender,
            "blood_group": employee.blood_group,
            "address": employee.address,
            "profile_photo": employee.profile_photo.url if employee.profile_photo else None,
        })

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            **employee_data,  # Include the employee data if available
        })
    
