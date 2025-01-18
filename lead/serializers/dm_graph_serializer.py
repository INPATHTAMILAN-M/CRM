from rest_framework import serializers

class LeadCountRequestSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
