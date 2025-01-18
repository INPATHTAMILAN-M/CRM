from rest_framework import viewsets

from accounts.filters.salutation_filter import SalutationFilter
from ..models import Salutation
from ..serializers.salutation_serializer import SalutationSerializer
from rest_framework import status
from rest_framework.response import Response
from django_filters import rest_framework as filters

class SalutationViewSet(viewsets.ModelViewSet):
    queryset = Salutation.objects.all()
    serializer_class = SalutationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SalutationFilter

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