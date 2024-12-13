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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )