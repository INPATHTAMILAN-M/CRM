from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Vertical
from lead.filters.vertical_filter import VerticalFilter
from ..serializers.vertical_serializer import VerticalSerializer

class VerticalViewSet(viewsets.ModelViewSet):
    queryset = Vertical.objects.all()
    serializer_class = VerticalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VerticalFilter
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )