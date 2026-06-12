from django.urls import path
from lead.viewsets.assignment_notification_viewset import AssignedNotificationAPIView
from lead.viewsets.calendar_sync_viewset import CalendarSyncAPIView
from lead.viewsets.contact_viewset import ImportContactsAPIView, ImportLeadsAPIView, BulkImportAPIView
from .routers import router
from .views import get_apollo_leads

urlpatterns = [
    path('import_contacts/', ImportContactsAPIView.as_view(), name='import_contacts'),
    path('import-leads/', ImportLeadsAPIView.as_view(), name='import_leads'),
    path('calendar-sync/', CalendarSyncAPIView.as_view(), name='calendar_sync'),
    path('assignment_notification/', AssignedNotificationAPIView.as_view(), name='assigned_notifications'),
    path('bulk_import/', BulkImportAPIView.as_view(), name='bulk_import'),
    path('apollo-leads/fetch/', get_apollo_leads, name='get_apollo_leads'),
]