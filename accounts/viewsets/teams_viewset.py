from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from accounts.filters.teams_filter import TeamsFilter
from accounts.models import Teams
from accounts.serializers.teams_serializer import TeamsCreateSerializer, TeamsListSerializer, TeamsUpdateSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class TeamsViewSet(viewsets.ModelViewSet):
    queryset = Teams.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TeamsFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeamsListSerializer  
        elif self.action == 'update' or self.action == 'partial_update':
            return TeamsUpdateSerializer
        return TeamsCreateSerializer  
    
