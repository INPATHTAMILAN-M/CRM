from rest_framework import viewsets
from ..models import Salutation
from ..serializers.salutation_serializer import SalutationSerializer

class SalutationViewSet(viewsets.ModelViewSet):
    queryset = Salutation.objects.all()
    serializer_class = SalutationSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Override the destroy method to set is_active to False instead of deleting the record.
        """
        salutation = self.get_object()
        salutation.is_active = False
        salutation.save()

        # Return a success response
        return Response({"status": "success", "message": "Salutation deactivated successfully."}, status=status.HTTP_200_OK)