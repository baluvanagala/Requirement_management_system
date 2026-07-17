from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, LogoutSerializer, UserSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, BlacklistedToken
from datetime import datetime, timezone


#######
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail

# Create your views here.

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response(serializer.errors, status=400)
    

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)

            try:
                user = CustomUser.objects.get(id=token["user_id"])
            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "Invalid refresh token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            expires_at = datetime.fromtimestamp(
                token["exp"],
                tz=timezone.utc
            )

            if BlacklistedToken.objects.filter(token=refresh_token).exists():
                return Response(
                    {"message": "Token already blacklisted."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            BlacklistedToken.objects.create(
                user=user,
                token=refresh_token,
                expires_at=expires_at
            )

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    



class UserAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            try:
                user = CustomUser.objects.get(id=pk)
            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = UserSerializer(user)
            return Response(serializer.data)

        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User created successfully",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
    
