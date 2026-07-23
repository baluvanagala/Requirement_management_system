<<<<<<< HEAD
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, LogoutSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from .models import CustomUser, BlacklistedToken
from datetime import datetime, timezone

import logging

logger = logging.getLogger(__name__)


from .response_utils import (
    response_success,
    response_created,
    response_bad_request,
    response_not_found,
    response_server_error,
)

# Create your views here.


class LoginView(APIView):
    """
    Login API

    Authenticates a user using email/phone and password.
    Returns JWT access and refresh tokens on successful login.
    """

    def post(self, request):
        """
        Authenticate a user and generate JWT tokens.

        Validates the provided credentials and returns
        access and refresh tokens if authentication
        is successful.
        """

        try:
            serializer = LoginSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.validated_data["user"]

                refresh = RefreshToken.for_user(user)

                logger.info(f"User login successful. User ID: {user.id}")

                return response_success(
                    message="Login successful",
                    data={
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                )
            logger.warning(f"Login Validation failed. Errors: {serializer.errors}")

            return response_bad_request(
                data=serializer.errors, message="Validation failed"
            )
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)

            return response_server_error(message="An unexpected error occurred.")


class LogoutView(APIView):
    """
    Logout API.

    Blacklists the provided refresh token to prevent
    further use and effectively logs out the user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Logout a user.

        Validates the refresh token, checks whether it
        has already been blacklisted, and stores it in
        the blacklist to invalidate future usage.
        """
        try:
            serializer = LogoutSerializer(data=request.data)

            if serializer.is_valid():
                refresh_token = serializer.validated_data["refresh"]
                token = RefreshToken(refresh_token)

                try:
                    user = CustomUser.objects.get(id=token["user_id"])
                except CustomUser.DoesNotExist:
                    logger.warning("Logout failed. User not found for refresh token.")

                    return response_bad_request(message="Invalid refresh token.")

                expires_at = datetime.fromtimestamp(token["exp"], tz=timezone.utc)

                if BlacklistedToken.objects.filter(token=refresh_token).exists():
                    logger.warning(f"Token already blacklisted. User ID: {user.id}")
                    return response_bad_request(message="Token already blacklisted.")

                BlacklistedToken.objects.create(
                    user=user, token=refresh_token, expires_at=expires_at
                )

                logger.info(f"Logout successful. User ID: {user.id}")

                return response_success(message="Logout successful.")
            logger.warning(f"Logout validation failed. Errors: {serializer.errors}")
            return response_bad_request(
                message="Validation failed", data=serializer.errors
            )
        except Exception as e:
            logger.error(f"Unexcepted error during logout: {str(e)}", exc_info=True)
            return response_server_error(message="An unexpected error occurred.")


class UserAPIView(APIView):
    """
    Handles user-related operations such as
    creating and retrieving user information.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        """
        Retrieve user details.

        Returns a specific user if an ID is provided,
        otherwise returns all users.
        """
        try:
            if pk:
                try:
                    user = CustomUser.objects.get(id=pk)
                except CustomUser.DoesNotExist:
                    logger.warning(f"User not found. User ID: {pk}")

                    return response_not_found(message="User not found.")

                serializer = UserSerializer(user)

                logger.info(f"User retrieved successfully. User ID: {pk}")

                return response_success(
                    message="User retrieved successfully.", data=serializer.data
                )

            users = CustomUser.objects.all()
            serializer = UserSerializer(users, many=True)

            logger.info(f"Retrieved all users. Total users: {users.count()}")

            return response_success(
                message="Users retrieved successfully.", data=serializer.data
            )
        except Exception as e:
            logger.error(
                f"Unexpected error while retrieving users: {str(e)}", exc_info=True
            )

            return response_server_error(message="An unexpected error occurred.")

    def post(self, request):
        """
        Create a new user.

        Validates the request data and creates
        a new user record in the database.
        """
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()

                logger.info(f"User created successfully. User ID: {user.id}")

                return response_created(
                    message="User created successfully.", data=UserSerializer(user).data
                )
            logger.warning(f"User creation failed. Errors: {serializer.errors}")

            return response_bad_request(
                message="Validation failed", data=serializer.errors
            )
        except Exception as e:
            logger.error(
                f"Unexpected error while creating user: {str(e)}", exc_info=True
            )

            return response_server_error(message="An unexpected error occurred.")
=======
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
>>>>>>> register_api
