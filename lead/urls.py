from django.urls import path
from lead.viewsets.contact_viewset import ImportContactsAPIView, ImportLeadsAPIView
from .routers import router

urlpatterns = [

    path('import_contacts/', ImportContactsAPIView.as_view(), name='import_contacts'),
    path('import-leads/', ImportLeadsAPIView.as_view(), name='import_leads'),
]