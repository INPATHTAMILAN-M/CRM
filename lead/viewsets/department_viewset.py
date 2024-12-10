from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Department
from ..serializers.department_serializer import DepartmentSerializer
from ..filters.department_filter import DepartmentFilter

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = (DjangoFilterBackend,)  # Specify the filter backend
    filterset_class = DepartmentFilter  # Use the filter class here
