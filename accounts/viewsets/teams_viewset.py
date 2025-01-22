from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from accounts.filters.teams_filter import TeamsFilter
from accounts.models import Teams
from accounts.serializers.teams_serializer import TeamsCreateSerializer, TeamsFilterSerializer, TeamsListSerializer, TeamsUpdateSerializer, UserSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from lead.custompagination import Paginator

class TeamsViewSet(viewsets.ModelViewSet):
    queryset = Teams.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamsFilter
    pagination_class = Paginator
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeamsListSerializer  
        elif self.action == 'update' or self.action == 'partial_update':
            return TeamsUpdateSerializer
        return TeamsCreateSerializer  

# viewset.py

class TeamsFilterViewSet(viewsets.ModelViewSet):
    queryset = Teams.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamsFilter
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer  # Serialize bde_user as individual User objects

    def list(self, request, *args, **kwargs):
        # Apply filtering via the filter backend (preserving the teams queryset)
        queryset = self.filter_queryset(self.get_queryset())

        # Flatten the bde_user data from the queryset
        bde_users = []
        for team in queryset:
            bde_users.extend(team.bde_user.all())

        # Handle pagination
        page = self.paginate_queryset(bde_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Return all bde_users if no pagination is needed
        serializer = self.get_serializer(bde_users, many=True)
        return Response(serializer.data)
