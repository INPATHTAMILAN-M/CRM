from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('userdetails/',UserProfileView.as_view(),name='user_profile'),

    # retrive lead source and from
    path('retrieve_lead_source/', RetrieveLeadSource.as_view(), name='retrieve_lead_source'),
    path('retrieve_lead_source_from/<int:source_id>/', RetrieveLeadSourceFrom.as_view(), name='retrieve_lead_source_from'),

]