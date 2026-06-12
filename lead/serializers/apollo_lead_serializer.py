from rest_framework import serializers
from lead.models import ApolloLead


class ApolloLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApolloLead
        fields = '__all__'
        read_only_fields = ('created_on','updated_on')
