from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from ..google_calendar import sync_google_events


class CalendarSyncAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return self.sync_calendar()

    def post(self, request, *args, **kwargs):
        return self.sync_calendar()

    def sync_calendar(self):
        try:
            count = sync_google_events()
            return Response(
                {
                    'detail': 'Google Calendar sync completed successfully.',
                    'synced_tasks': count,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return Response(
                {
                    'detail': 'Google Calendar sync failed.',
                    'error': str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
