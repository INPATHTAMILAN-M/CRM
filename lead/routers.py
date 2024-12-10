from rest_framework.routers import DefaultRouter

from accounts.viewsets.users_viewset import GetLeadOwnerViewSet, UsersForLeadViewSet
from lead.viewsets.contact_viewset import ContactViewSet
from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.source_from_viewset import LeadSourceFromViewSet
from lead.viewsets.source_viewset import LeadSourceViewSet
from lead.viewsets.lead_viewset import LeadViewSet
from lead.viewsets.opportunity_viewset import OpportunityViewset
from lead.viewsets.log_viewset import LogViewSet
from lead.viewsets.stage_viewset import StageViewSet
from lead.viewsets.focuse_segmant_viewset import FocusSegmentViewSet


# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'lead', LeadViewSet)
router.register(r'opportunity', OpportunityViewset)
router.register(r'lead_sources', LeadSourceViewSet)
router.register(r'lead_sources_from', LeadSourceFromViewSet)
router.register(r'log', LogViewSet)
router.register(r'stage', StageViewSet)
router.register(r'lead_statuses', LeadStatusViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'users_for_lead', UsersForLeadViewSet)
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')
router.register(r'focuse_segmant',FocusSegmentViewSet)
router.register(r'contact', ContactViewSet, basename='contact')



urlpatterns = router.urls