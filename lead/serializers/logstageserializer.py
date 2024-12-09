from rest_framework import serializers
from ..models import Log_Stage

class LogStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage']
