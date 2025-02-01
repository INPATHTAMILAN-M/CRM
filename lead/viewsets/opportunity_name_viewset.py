
from rest_framework import viewsets, status
from rest_framework.response import Response
from lead.models import Opportunity_Name
from lead.custompagination import Paginator
from ..serializers.opportunity_name_serializer import (
    OpportunityNameSerializer,
    OpportunityNameCreateSerializer,
    OpportunityNameUpdateSerializer,
    OpportunityNameListSerializer,
    OpportunityNameRetrieveSerializer
)

class OpportunityNameViewSet(viewsets.ModelViewSet):
    queryset = Opportunity_Name.objects.filter(is_active=True)
    serializer_class = OpportunityNameSerializer
    pagination_class = Paginator
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OpportunityNameCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return OpportunityNameUpdateSerializer
        elif self.action == 'list':
            return OpportunityNameListSerializer
        elif self.action == 'retrieve':
            return OpportunityNameRetrieveSerializer
        return OpportunityNameSerializer


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        return Response(status=status.HTTP_204_NO_CONTENT)
