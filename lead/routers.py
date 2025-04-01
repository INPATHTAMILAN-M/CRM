from rest_framework.routers import DefaultRouter

from accounts.viewsets.city_viewset import CityViewSet
from accounts.viewsets.salutation_viewset import SalutationViewSet
from accounts.viewsets.teams_viewset import TeamsFilterViewSet, TeamsViewSet
from accounts.viewsets.users_viewset import AllUsersViewSet, GetBdeUserViewSet, GetDmUserViewSet, GetLeadOwnerViewSet, GetOwnerUserViewSet, GetTaskAssignedToUserViewSet, UsersForLeadViewSet
from lead.viewsets.contact_status_viewset import ContactStatusViewSet
from lead.viewsets.contact_viewset import ContactViewSet
from lead.viewsets.country_viewset import CountryViewSet
from lead.viewsets.dashboard_count_viewset import LeadStatusCountViewSet
from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.dm_graph_viewset import LeadCountViewSet
from lead.viewsets.lead_assignment_viewset import LeadAssignmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.market_segment_viewset import MarketSegmentViewSet
from lead.viewsets.note_viewset import NoteViewSet
from lead.viewsets.notification_viewset import NotificationViewSet
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
from lead.viewsets.task_viewset import CalanderTaskViewSet, TaskViewSet
from lead.viewsets.lead_bucket_viewset import LeadBucketViewSet
from lead.viewsets.vertical_viewset import VerticalViewSet
from lead.viewsets.opportunity_name_viewset import OpportunityNameViewSet
from lead.viewsets.task_conversation_log_viewset import TaskConversationLogViewSet



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
router.register(r'all_users', AllUsersViewSet, basename='all_users')
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')
router.register(r'get_task_assinged_to', GetTaskAssignedToUserViewSet, basename='get_task_assinged_to')
router.register(r'get_bde_user', GetBdeUserViewSet, basename='get_bde_user')
router.register(r'get_owner_user', GetOwnerUserViewSet, basename='get_owner_user')
router.register(r'get_dm_user', GetDmUserViewSet, basename='get_dm_user')
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
router.register(r'verticals', VerticalViewSet)
router.register(r'City', CityViewSet)
router.register(r'calander_task', CalanderTaskViewSet, basename='calander_task')
router.register(r'bdm_team', TeamsViewSet)
router.register(r'bdm_bde_team', TeamsFilterViewSet, basename='bdm_bde_team')
router.register(r'dm_graph_counts', LeadCountViewSet, basename='dm_graph_counts')
router.register(r'opportunity-name', OpportunityNameViewSet, basename='opportunity-name')
router.register(r'task-conversation', TaskConversationLogViewSet, basename='task-conversation')
router.register(r'notifications', NotificationViewSet, basename='notification')

# in accounts
router.register(r'salutations', SalutationViewSet)
urlpatterns = router.urls