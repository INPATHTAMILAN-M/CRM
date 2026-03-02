from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..custom_pagination import Paginator
from ..models import ContentLog, Log
from ..serializers.log_serializer import *
from ..serializers.contentlog_serializer import ContentLogSerializer
from ..filters import log_filter
from rest_framework import status
from rest_framework.response import Response

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = log_filter.LogFilter
    pagination_class = Paginator
    alowed_methods = ['GET', 'POST', 'PATCH']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LogCreateSerializer
        if self.action == 'list':
            return LogListSerializer
        if self.action in ['update', 'partial_update']:
            return LogUpdateSerializer
        return LogListSerializer    

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        lead_id = request.query_params.get('lead')
        contact_id = request.query_params.get('contact') or request.query_params.get('contant')

        if request.query_params.get('contant') and not request.query_params.get('contact'):
            queryset = queryset.filter(contact_id=contact_id)

        should_merge_content_logs = bool(lead_id or contact_id)

        if not should_merge_content_logs:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        log_items = self.get_serializer(queryset, many=True).data

        content_logs = ContentLog.objects.all()
        if lead_id:
            content_logs = content_logs.filter(lead_id=lead_id)
        if contact_id:
            content_logs = content_logs.filter(contact_id=contact_id)

        content_log_items = ContentLogSerializer(content_logs.order_by('-created_date'), many=True).data

        for item in log_items:
            item['log_source'] = 'log'
            item['log_timestamp'] = item.get('created_on')

        for item in content_log_items:
            item['log_source'] = 'content_log'
            item['log_timestamp'] = item.get('created_date')

        merged_items = sorted(
            [*log_items, *content_log_items],
            key=lambda item: item.get('log_timestamp') or '',
            reverse=True,
        )

        page = self.paginate_queryset(merged_items)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(merged_items)

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