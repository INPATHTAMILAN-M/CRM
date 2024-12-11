from rest_framework.routers import DefaultRouter

from accounts.viewsets.users_viewset import GetLeadOwnerViewSet, UsersForLeadViewSet
from lead.viewsets.contact_viewset import ContactViewSet
from lead.viewsets.country_viewset import CountryViewSet
from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.market_segment_viewset import MarketSegmentViewSet
from lead.viewsets.source_from_viewset import LeadSourceFromViewSet
from lead.viewsets.source_viewset import LeadSourceViewSet
from lead.viewsets.lead_viewset import LeadViewSet
from lead.viewsets.opportunity_viewset import OpportunityViewset
from lead.viewsets.log_viewset import LogViewSet
from lead.viewsets.stage_viewset import StageViewSet
from lead.viewsets.focuse_segmant_viewset import FocusSegmentViewSet
from lead.viewsets.log_stage_viewset import LogStageViewSet
from lead.viewsets.state_viewset import StateViewSet
from lead.viewsets.tag_viewset import TagViewSet
from lead.viewsets.task_viewset import TaskViewSet


# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'lead', LeadViewSet)
router.register(r'opportunity', OpportunityViewset)
router.register(r'lead_sources', LeadSourceViewSet)
router.register(r'lead_sources_from', LeadSourceFromViewSet)
router.register(r'log', LogViewSet)
router.register(r'log-stage', LogStageViewSet)
router.register(r'lead_statuses', LeadStatusViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'users_for_lead', UsersForLeadViewSet)
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')
router.register(r'focuse_segmant',FocusSegmentViewSet)
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'market_segments', MarketSegmentViewSet)
router.register(r'tags', TagViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'states', StateViewSet)
router.register(r'task',TaskViewSet,basename='tasks')



urlpatterns = router.urls