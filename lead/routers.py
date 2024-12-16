from rest_framework.routers import DefaultRouter

from accounts.viewsets.salutation_viewset import SalutationViewSet
from accounts.viewsets.users_viewset import GetLeadOwnerViewSet, UsersForLeadViewSet
from lead.viewsets.contact_status_viewset import ContactStatusViewSet
from lead.viewsets.contact_viewset import ContactViewSet
from lead.viewsets.country_viewset import CountryViewSet
from lead.viewsets.dashboard_count_viewset import LeadStatusCountViewSet
from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.lead_assignment_viewset import LeadAssignmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.market_segment_viewset import MarketSegmentViewSet
from lead.viewsets.note_viewset import NoteViewSet
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
from lead.viewsets.task_assignment_viewset import TaskAssignmentViewSet
from lead.viewsets.task_viewset import TaskViewSet
from lead.viewsets.lead_bucket_viewset import LeadBucketViewSet


# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'lead', LeadViewSet, basename='lead')
router.register(r'opportunity', OpportunityViewset, basename='opportunity')
router.register(r'lead_sources', LeadSourceViewSet, basename='lead_sources')
router.register(r'lead_sources_from', LeadSourceFromViewSet, basename='lead_sources_from')
router.register(r'log', LogViewSet, basename='log')
router.register(r'log-stage', LogStageViewSet, basename='log-stage')
router.register(r'lead_statuses', LeadStatusViewSet, basename='lead_statuses')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'users_for_lead', UsersForLeadViewSet, basename='users_for_lead')
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')
router.register(r'focuse_segmant', FocusSegmentViewSet, basename='focuse_segmant')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'market_segments', MarketSegmentViewSet, basename='market_segments')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'states', StateViewSet, basename='states')
router.register(r'stages', StageViewSet, basename='stages')
router.register(r'task', TaskViewSet, basename='tasks')
router.register(r'lead-bucket', LeadBucketViewSet, basename='lead-bucket')
router.register(r'lead_status_count', LeadStatusCountViewSet, basename='lead-status-count')
router.register(r'contact_statuses', ContactStatusViewSet)
router.register(r'task_assignments', TaskAssignmentViewSet)
router.register(r'notes', NoteViewSet)


# in accounts
router.register(r'salutations', SalutationViewSet)
urlpatterns = router.urls