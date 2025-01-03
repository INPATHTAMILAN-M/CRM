from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import Country
from lead.custompagination import Paginator
from lead.filters.country_filter import CountryFilter
from lead.serializers.lead_serializer import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CountryFilter
    pagination_class = Paginator
