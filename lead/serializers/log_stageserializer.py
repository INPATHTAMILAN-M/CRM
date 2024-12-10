from rest_framework import serializers
from ..models import Log_Stage

class GetLogStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = "__all__"
