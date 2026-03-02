from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from lead.custom_pagination import Paginator
from ..models import ContentLog
from ..serializers.contentlog_serializer import ContentLogSerializer, ContentLogCreateSerializer


class ContentLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact', 'created_by', 'proposal']

    def get_queryset(self):
        return ContentLog.objects.all().select_related('contact', 'created_by')

    def get_serializer_class(self):
        if self.action == 'create':
            return ContentLogCreateSerializer
        return ContentLogSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
