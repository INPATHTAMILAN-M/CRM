from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.filters.city_filter import CityFilter
from accounts.serializers.city_serializer import CitySerializer
from lead.custompagination import Paginator

from ..models import City

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CityFilter
    pagination_class = Paginator
    