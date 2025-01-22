from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.filters.city_filter import CityFilter
from accounts.serializers.city_serializer import  CreateCitySerializer, GetCitySerializer
from lead.custompagination import Paginator

from ..models import City

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('-id')
    # serializer_class = CitySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CityFilter
    pagination_class = Paginator
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCitySerializer
        if self.action == 'list':
            return GetCitySerializer
        if self.action in ['update', 'partial_update']:
            return CreateCitySerializer
        return GetCitySerializer  
