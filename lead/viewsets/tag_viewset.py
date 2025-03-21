from rest_framework import viewsets
from django_filters import rest_framework as filters

from accounts.models import Tag
from lead.custom_pagination import Paginator
from lead.filters.tag_filter import TagFilter
from lead.serializers.tag_serializer import TagSerializer
from rest_framework import status
from rest_framework.response import Response
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TagFilter
    pagination_class = Paginator
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_active = request.data.get('is_active')
        instance.is_active = is_active
        instance.save()

        if is_active == 'True':
            return Response(
                {"detail": "Activated Successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Deactivated Successfully."},
                status=status.HTTP_200_OK
            )