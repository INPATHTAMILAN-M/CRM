from rest_framework import viewsets
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


# ViewSet for Lead Owner based on BDM group
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