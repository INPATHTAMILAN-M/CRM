from ..models import Log_Stage
from rest_framework import serializers

class StageRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']

class StageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']

class StageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']


class StageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']