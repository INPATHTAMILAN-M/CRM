from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.contrib.auth.models import User, Group
from accounts.filters.users_filter import UserFilter
from lead.custom_pagination import Paginator
from ..serializers.user_serializer import UserSerializer

# ViewSet for Users for Lead
class AllUsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator
    http_method_names = ['get', 'post', 'patch', 'delete']

    def partial_update(self, request, *args, **kwargs):
        """
        Override PATCH method to update both User and Employee fields.
        
        Accepts:
        - first_name, last_name, email, username (User fields)
        - phone_number, country_code_id, department_id, designation_id, 
          gender, blood_group, address, joined_on, profile_photo (Employee fields)
        """
        from lead.models import Employee
        
        user = self.get_object()
        data = request.data
        
        # Update User model fields
        user_fields = ['first_name', 'last_name', 'email', 'username']
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
        
        try:
            user.full_clean()
            user.save()
        except Exception as e:
            return Response(
                {'error': f'User update failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update Employee model fields if they exist in request
        employee_fields = [
            'phone_number', 'country_code_id', 'department_id', 
            'designation_id', 'gender', 'blood_group', 'address', 'joined_on'
        ]
        
        if any(field in data for field in employee_fields) or 'profile_photo' in request.FILES:
            try:
                employee = user.employee
                
                for field in employee_fields:
                    if field in data:
                        setattr(employee, field, data[field])
                
                # Handle profile photo separately if provided
                if 'profile_photo' in request.FILES:
                    employee.profile_photo = request.FILES['profile_photo']
                
                employee.full_clean()
                employee.save()
                
            except Employee.DoesNotExist:
                return Response(
                    {'error': 'Employee profile not found for this user.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': f'Employee update failed: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Return updated user data
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UsersForLeadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter users that belong to the target groups TM, BDE, or Tele Marketer
        target_groups = Group.objects.filter(name__in=["TM", "Tele Marketer"])
        return queryset.filter(groups__in=target_groups).distinct()

class GetLeadOwnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter users that belong to the target group BDM
        target_groups = Group.objects.filter(name="BDM")
        return queryset.filter(groups__in=target_groups).distinct()

class GetTaskAssignedToUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter users that belong to the target group BDM
        target_groups = Group.objects.filter(name__in=["BDM","BDE"])
        return queryset.filter(groups__in=target_groups).distinct()
    
class GetBdeUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["BDE"])
        return queryset.filter(groups__in=target_groups).distinct()
    
class GetDmUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["DM"])
        return queryset.filter(groups__in=target_groups).distinct()

class GetOwnerUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["Admin"])
        return queryset.filter(groups__in=target_groups).distinct()