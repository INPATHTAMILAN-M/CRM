from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import Tag
from lead.custompagination import Paginator
from lead.filters.tag_filter import TagFilter
from lead.serializers.lead_serializer import TagSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TagFilter
    pagination_class = Paginator