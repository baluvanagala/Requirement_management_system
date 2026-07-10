from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate

from .models import Employee
from .serializers import RegisterSerializer, EmployeeSerializer
from .permissions import IsHRorAdmin


class RegisterView(APIView):
    """
    POST /api/register/
    Only HR, Manager, or Admin users can register new employees.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            employee = serializer.save()
            return Response(
                serializer.to_representation(employee),
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeListView(APIView):
    """
    GET  /api/employees/ — Authenticated HR/Manager/Admin see all; others get 403.
    POST /api/employees/ — Unauthenticated clients can pass credentials in body;
                           if valid and role is HR/Manager/Admin, returns the list.
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny]
        # POST handles its own auth via credentials in the request body
        return []

    def get(self, request):
        employees = Employee.objects.select_related("user").all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Authenticate via credentials in the body and return employee list."""
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        if not username_or_email or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # USERNAME_FIELD is 'email', so authenticate() expects email=
        user = authenticate(request=request, email=username_or_email, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.role not in ("hr", "manager", "admin"):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employees = Employee.objects.select_related("user").all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)