
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lead.models import Lead_Bucket
from ..serializers.lead_bucket_serializers import *
from ..custom_pagination import Paginator

class LeadBucketViewSet(viewsets.ModelViewSet):
    queryset = Lead_Bucket.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action == 'create':
            return LeadBucketCreateSerializer
        if self.action == 'list':
            return LeadBucketListSerializer
        if self.action in ['update', 'partial_update']:
            return LeadBucketUpdateSerializer
        return LeadBucketDetailSerializer

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