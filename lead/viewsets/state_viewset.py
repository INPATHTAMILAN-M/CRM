
from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import State
from lead.custom_pagination import Paginator
from lead.filters.state_filter import StateFilter
from lead.serializers.state_serializer import CreateStateSerializer, GetStateSerializer


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all().order_by('-id')
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StateFilter
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateStateSerializer
        if self.action == 'list':
            return GetStateSerializer
        if self.action in ['update', 'partial_update']:
            return CreateStateSerializer
        return GetStateSerializer  
