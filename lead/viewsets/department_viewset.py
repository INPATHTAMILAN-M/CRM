from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from lead.custompagination import Paginator
from ..models import Department
from ..serializers.department_serializer import DepartmentSerializer
from ..filters.department_filter import DepartmentFilter

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = (DjangoFilterBackend,) 
    filterset_class = DepartmentFilter 
    pagination_class = Paginator