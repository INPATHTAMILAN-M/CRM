from rest_framework import serializers
from ..models import Tag


# Serializer for Tag
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
