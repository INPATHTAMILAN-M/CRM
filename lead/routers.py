from rest_framework.routers import DefaultRouter

from lead.viewsets.department_viewset import DepartmentViewSet
from lead.viewsets.lead_status_viewset import LeadStatusViewSet
from lead.viewsets.source_from_viewset import LeadSourceFromViewSet
from lead.viewsets.source_viewset import LeadSourceViewSet
from .viewsets import lead_viewset, opportunity_viewset,log_viewset, stage_viewset

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

urlpatterns = router.urls