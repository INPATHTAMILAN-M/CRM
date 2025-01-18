from rest_framework import serializers
from accounts.models import Focus_Segment, Vertical
from django.contrib.auth.models import User

class VerticalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertical
        fields = '__all__'  # Or specify a list of fields like ['id', 'vertical', 'description', 'is_active']

class GetFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'

class PostFocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = '__all__'

class ListFocusSegmentSerializer(serializers.ModelSerializer):
    vertical = VerticalSerializer()
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