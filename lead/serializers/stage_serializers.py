from ..models import Stage
from rest_framework import serializers

class StageRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'is_active']

class StageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'is_active']

class StageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'is_active']


class StageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'stage', 'description', 'is_active']