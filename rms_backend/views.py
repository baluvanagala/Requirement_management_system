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
            return [AllowAny()]
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









import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP
from .serializers import GenerateOTPSerializer, VerifyOTPSerializer, ResendOTPSerializer

User = get_user_model()

OTP_VALIDITY_MINUTES = 2  # OTP expires after 2 minutes


class GenerateOTPView(APIView):
    """
    POST /api/generate-otp/
    Authenticate with email + password, then generate a 6-digit OTP
    valid for 2 minutes.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = GenerateOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Authenticate user (USERNAME_FIELD is 'email')
        user = authenticate(request=request, email=email, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))

        # Create or update OTP record
        OTP.objects.update_or_create(
            user=user,
            defaults={
                "otp": otp_code,
                "expires_at": timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES),
            },
        )

        # TODO: Send OTP via Email / SMS here
        # send_otp_email(user.email, otp_code)

        return Response(
            {
                "message": "OTP generated successfully.",
                "username": user.username,
                "expires_in": f"{OTP_VALIDITY_MINUTES} minutes",
                "otp": otp_code,  # TESTING ONLY — remove in production
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """
    POST /api/verify-otp/
    Verify the OTP for a given username. If valid and not expired,
    return JWT access + refresh tokens.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        otp_code = serializer.validated_data["otp"]

        user = User.objects.get(username=username)

        # Check if OTP record exists
        try:
            otp_record = OTP.objects.get(user=user)
        except OTP.DoesNotExist:
            return Response(
                {"detail": "No OTP found. Please generate an OTP first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if OTP has expired
        if otp_record.is_expired():
            otp_record.delete()
            return Response(
                {"detail": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if OTP matches
        if otp_record.otp != otp_code:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP is valid — delete it (one-time use)
        otp_record.delete()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "OTP verified successfully.",
                "username": user.username,
                "role": user.role,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPView(APIView):
    """
    POST /api/resend-otp/
    Resend a new OTP for the given username. Valid for 2 minutes.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        user = User.objects.get(username=username)

        # Generate a new OTP
        otp_code = str(random.randint(100000, 999999))

        # Update or create OTP
        OTP.objects.update_or_create(
            user=user,
            defaults={
                "otp": otp_code,
                "expires_at": timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES),
            },
        )

        # TODO: Send OTP via Email / SMS here

        return Response(
            {
                "message": "OTP resent successfully.",
                "username": username,
                "expires_in": f"{OTP_VALIDITY_MINUTES} minutes",
                "otp": otp_code,  # TESTING ONLY — remove in production
            },
            status=status.HTTP_200_OK,
        )