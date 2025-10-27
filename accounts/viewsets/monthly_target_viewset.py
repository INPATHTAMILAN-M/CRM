from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.contrib.auth.models import Group
from accounts.models import MonthlyTarget
from accounts.serializers.monthly_target_serializer import MonthlyTargetSerializer
from lead.custom_pagination import Paginator


class MonthlyTargetViewSet(viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all().order_by('-year', '-month')
    serializer_class = MonthlyTargetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['user', 'month', 'year']
    http_method_names = ['get', 'post','patch', 'delete']
    pagination_class = Paginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            # Admins can see all
            return super().get_queryset()
        else:
            # Non-admins can only see their own targets
            return super().get_queryset().filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            # Admins can create for any user
            serializer.save()
        else:
            # Non-admins can only create for themselves
            serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.groups.filter(name='Admin').exists() or instance.user == user:
            # Admins can update any, users can update their own
            serializer.save()
        else:
            # Forbidden
            return Response({"detail": "You do not have permission to update this target."}, status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.groups.filter(name='Admin').exists() or instance.user == user:
            # Admins can delete any, users can delete their own
            instance.delete()
        else:
            # Forbidden
            return Response({"detail": "You do not have permission to delete this target."}, status=status.HTTP_403_FORBIDDEN)