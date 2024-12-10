from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Focus_Segment
from ..serializers.focus_segmant_serializers import GetFocusSegmentSerializer, PostFocusSegmentSerializer, PatchFocusSegmentSerializer, ListFocusSegmentSerializer
from ..filters.lead_status_filter import LeadStatusFilter

class FocusSegmentViewSet(viewsets.ModelViewSet):
    queryset = Focus_Segment.objects.all()
    filter_backends = (DjangoFilterBackend,)  # Specify the filter backend
    filterset_class = LeadStatusFilter  # Use the filter class here

    def get_serializer_class(self):
        if self.action == 'create':
            return PostFocusSegmentSerializer
        if self.action == 'list':
            return ListFocusSegmentSerializer
        if self.action in ['update', 'partial_update']:
            return PatchFocusSegmentSerializer
        return GetFocusSegmentSerializer  