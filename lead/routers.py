from rest_framework.routers import DefaultRouter
from .viewsets import lead_viewset, opportunity_viewset

# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'lead', lead_viewset.ViewSet)
router.register(r'opportunity', opportunity_viewset.ViewSet)

urlpatterns = router.urls
