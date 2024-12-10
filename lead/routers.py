from rest_framework.routers import DefaultRouter

from accounts.viewsets.users_viewset import GetLeadOwnerViewSet, UsersForLeadViewSet
from lead.viewsets.contact_viewset import ContactViewSet
from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.source_from_viewset import LeadSourceFromViewSet
from lead.viewsets.source_viewset import LeadSourceViewSet
from .viewsets import lead_viewset, opportunity_viewset,log_viewset, stage_viewset, focuse_segmant_viewset

# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'lead', lead_viewset.ViewSet)
router.register(r'opportunity', opportunity_viewset.ViewSet)
router.register(r'lead_sources', LeadSourceViewSet)
router.register(r'lead_sources_from', LeadSourceFromViewSet)
router.register(r'log', log_viewset.LogViewSet)
router.register(r'stage', stage_viewset.StageViewSet)
router.register(r'lead_statuses', LeadStatusViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'users_for_lead', UsersForLeadViewSet)
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')
router.register(r'contacts', ContactViewSet)
# router.register(r'focuse_segmant',focuse_segmant_viewset)


urlpatterns = router.urls