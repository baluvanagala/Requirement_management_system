import random
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer
from .models import User


class EmailOrPhoneRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            if user.email:
                message = "OTP sent to email."
                send_mail(
                    subject="Your OTP Verification Code",
                    message=f"Your OTP is {otp}.",
                    from_email="noreply@example.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            else:
                message = "OTP sent to phone number."

            return Response(
                {
                    "email": user.email,
                    "message": message,
                    "user_id": user.user_id,
                    "email_verified": user.email_verified,
                    "phone_verified": user.phone_verified,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response(
                {"error": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.otp == otp:
            user.is_verified = True
            user.email_verified = True
            user.is_active = True
            user.save()
            return Response(
                {"message": "OTP verified successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response(
                {"error": "Identifier and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Look up by email or phone number
        try:
            user = User.objects.get(Q(email=identifier) | Q(phone_number=identifier))
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.check_password(password):
            return Response(
                {
                    "message": "Login successful.",
                    "email": user.email,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )