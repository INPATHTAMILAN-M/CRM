from rest_framework.routers import DefaultRouter

from accounts.viewsets.users_viewset import GetLeadOwnerViewSet, UsersForLeadViewSet

router = DefaultRouter()

router.register(r'users_for_lead', UsersForLeadViewSet)
router.register(r'get_lead_owner', GetLeadOwnerViewSet, basename='get_lead_owner_unique')

urlpatterns = router.urls