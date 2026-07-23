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
