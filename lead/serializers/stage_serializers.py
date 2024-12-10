from ..models import Log_Stage
from rest_framework import serializers

class GetStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']

class PostStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']

class PatchStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']


class ListStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log_Stage
        fields = ['id', 'stage', 'description', 'is_active']