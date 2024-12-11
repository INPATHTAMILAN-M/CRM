
from rest_framework import serializers
from ..models import Lead_Bucket

class LeadBucketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Bucket
        fields = ['name', 'description']

class LeadBucketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Bucket
        fields = ['name', 'description']

class LeadBucketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Bucket
        fields = ['name', 'description']

class LeadBucketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Bucket
        fields = ['name', 'description']
