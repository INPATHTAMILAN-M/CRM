from rest_framework.routers import DefaultRouter
from .views import LeadViewSet

# Create a router and register the LeadViewSet
router = DefaultRouter()
router.register(r'leads', LeadViewSet)

# If you have any custom actions like 'opportunities', it will be automatically handled by the router

urlpatterns = router.urls
