# serializers.py

from rest_framework import serializers
from ..models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department']  # Specify the fields you want to include in the response
