from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer,LogoutSerializer,ForgotPasswordSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser

#######
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            serializer.blacklist_token()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# class ForgotPasswordView(APIView):

#     def post(self,request):
#         serializer=ForgotPasswordSerializer(data=request.data)

#         if serializer.is_valid():
#             email=serializer.validated_data['email']

#             try:
#                 user=CustomUser.objects.get(email=email)
#             except CustomUser.DoesNotExist:
#                 return Response(
#                     {'email':'Email is not registered.'},status=400
#                 )
#             uid=urlsafe_base64_encode(force_bytes(user.pk))

#             token=default_token_generator.make_token(user)

#             reset_link=(
#                 f'http://127:0.0.1:8000/reset-password/{uid}/{token}/'
#             )

#             send_mail(
#                 subject='password Reset',
#                 message=f'Click the link below: \n\n {reset_link}',
#                 from_email='baluvanagala66@gmail.com',
#                 recipient_list=[mail]

#             )

