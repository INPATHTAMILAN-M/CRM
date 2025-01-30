from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import *

# admin.site.register(OutstandingToken)
# admin.site.register(BlacklistedToken)
admin.site.register(Salutation)
admin.site.register(Vertical)
admin.site.register(Focus_Segment)
admin.site.register(Market_Segment)
admin.site.register(Tag)
admin.site.register(Contact_Status)
admin.site.register(Stage)
admin.site.register(Log_Stage)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Lead_Source)
admin.site.register(Lead_Source_From)
admin.site.register(User_Group)
admin.site.register(City)
admin.site.register(Teams)
