
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lead.models import Lead_Bucket
from ..serializers.lead_bucket_serializers import *
from ..custompagination import Paginator

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
