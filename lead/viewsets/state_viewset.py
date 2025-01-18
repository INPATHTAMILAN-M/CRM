
from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import State
from lead.custompagination import Paginator
from lead.filters.state_filter import StateFilter
from lead.serializers.state_serializer import StateSerializer


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StateFilter
    pagination_class = Paginator