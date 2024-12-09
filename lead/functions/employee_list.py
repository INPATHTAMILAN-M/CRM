from django.http import JsonResponse
from django.contrib.auth.models import User
from ..serializers.employeeserializer import EmployeeSerializer

def get_employee_list(request):
    employees = User.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)
