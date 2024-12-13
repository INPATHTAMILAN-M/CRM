from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from lead.custompagination import Paginator
from ..models import Focus_Segment
from ..serializers.focus_segmant_serializers import GetFocusSegmentSerializer, PostFocusSegmentSerializer, PatchFocusSegmentSerializer, ListFocusSegmentSerializer
from ..filters.focus_segment_filters import FocusSegmentFilter

class FocusSegmentViewSet(viewsets.ModelViewSet):
    queryset = Focus_Segment.objects.all()
    filter_backends = (DjangoFilterBackend,)  # Specify the filter backend
    filterset_class = FocusSegmentFilter  # Use the filter class here
    pagination_class = Paginator

    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostFocusSegmentSerializer
        if self.action == 'list':
            return ListFocusSegmentSerializer
        if self.action in ['update', 'partial_update']:
            return PatchFocusSegmentSerializer
        return GetFocusSegmentSerializer  

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        instance.is_active = False
        instance.save()

        return Response(
            {"detail": "Deactivated Successfully."},
            status=status.HTTP_200_OK
        )