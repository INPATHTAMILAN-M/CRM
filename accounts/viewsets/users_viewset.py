from rest_framework import viewsets
from django_filters import rest_framework as filters
from django.contrib.auth.models import User, Group
from accounts.filters.users_filter import UserFilter
from ..serializers.user_serializer import UserSerializer

# ViewSet for Users for Lead
class UsersForLeadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter users that belong to the target groups TM, BDE, or Tele Marketer
        target_groups = Group.objects.filter(name__in=["TM", "BDE", "Tele Marketer"])
        return queryset.filter(groups__in=target_groups).distinct()


# ViewSet for Lead Owner based on BDM group
class GetLeadOwnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter users that belong to the target group BDM
        target_groups = Group.objects.filter(name="BDM")
        return queryset.filter(groups__in=target_groups).distinct()
