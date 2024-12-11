from rest_framework import serializers
from accounts.models import Focus_Segment
from django.contrib.auth.models import User

class GetFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'

class PostFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'

class ListFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'

class PatchFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'
        extra_kwargs = {
            field: {'required': False} for field in Focus_Segment._meta.fields
        }