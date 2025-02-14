from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import Country
from lead.custom_pagination import Paginator
from lead.filters.country_filter import CountryFilter
from lead.serializers.country_serializer import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('-id')
    serializer_class = CountrySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CountryFilter
    pagination_class = Paginator
