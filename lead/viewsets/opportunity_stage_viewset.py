from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lead.models import Opportunity_Stage
from ..serializers.opportunity_stage_serializers import *


class OpportunityStageViewSet(viewsets.ModelViewSet):
    queryset = Opportunity_Stage.objects.all().order_by('-id')
    serializer_class = OpportunityStageListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OpportunityStageCreateSerializer
        if self.action == 'list':
            return OpportunityStageListSerializer
        if self.action in ['update', 'partial_update']:
            return OpportunityStageUpdateSerializer
        return OpportunityStageRetriveSerializer 

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(moved_by=self.request.user)
