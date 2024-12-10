from ..models import Stage
from rest_framework import serializers

class GetStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'probability', 'is_active']

class PostStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'probability', 'is_active']

class PatchStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'probability', 'is_active']


class ListStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'probability', 'is_active']