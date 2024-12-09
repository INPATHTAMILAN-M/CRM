from rest_framework.routers import DefaultRouter
from .viewsets import leadviewset, opportunityviewset

# Create a router and register the LeadViewSet
router = DefaultRouter()


router.register(r'leads', leadviewset.ViewSet)
router.register(r'opportunities', opportunityviewset.ViewSet)

# If you have any custom actions like 'opportunities', it will be automatically handled by the router

urlpatterns = router.urls
