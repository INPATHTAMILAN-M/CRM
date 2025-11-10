from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.contrib.auth.models import User, Group
from accounts.filters.users_filter import UserFilter
from lead.custom_pagination import Paginator
from ..serializers.user_serializer import (
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserDeleteSerializer
)

# ViewSet for Users for Lead
class AllUsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    from rest_framework import filters as drf_filters
    filter_backends = (filters.DjangoFilterBackend, drf_filters.SearchFilter)
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'username']
    pagination_class = Paginator
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'destroy':
            return UserDeleteSerializer
        return UserListSerializer  # default to list serializer

    def create(self, request, *args, **kwargs):
        """
        Create a new user with their profile.
        
        All UserProfile fields are now handled by the serializer automatically.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the created user with full details
        headers = self.get_success_headers(serializer.data)
        user = serializer.instance
        response_serializer = UserListSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        """
        Update user and their profile.
        
        The serializer now handles both User and UserProfile updates automatically.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return updated user with full details
        response_serializer = UserListSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

class UsersForLeadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
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
    serializer_class = UserListSerializer
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
    serializer_class = UserListSerializer
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
    serializer_class = UserListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["BDE"])
        return queryset.filter(groups__in=target_groups).distinct()
    
class GetDmUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["DM"])
        return queryset.filter(groups__in=target_groups).distinct()

class GetOwnerUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = Paginator

    def get_queryset(self):
        queryset = super().get_queryset()
        target_groups = Group.objects.filter(name__in=["Admin"])
        return queryset.filter(groups__in=target_groups).distinct()