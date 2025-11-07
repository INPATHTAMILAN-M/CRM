from rest_framework import serializers


class TargetAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for target analytics data.
    Used to display target vs achieved metrics for different time periods.
    """
    type = serializers.CharField()
    title = serializers.CharField()
    target = serializers.DecimalField(max_digits=10, decimal_places=2)
    achieved = serializers.DecimalField(max_digits=10, decimal_places=2)
    percentage = serializers.IntegerField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    increase = serializers.BooleanField()
    status = serializers.CharField(required=False, allow_null=True)
