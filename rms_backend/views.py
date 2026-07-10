from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rms_backend.serializers import ForgotPassword,RestPassword,ChangePassword

class Forgot(APIView):
    def post(self,request):
        serializer=ForgotPassword(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data['email']
            try:
                user=User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"Massege":"User not found"},status=status.HTTP_400_BAD_REQUEST
                )
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=PasswordResetTokenGenerator().make_token(user)
            reset_link=f"http://127.0.0.1:8000/api/reset-password/{uid}/{token}"

            send_mail(
                subject=f"Reset password",
                message=f"Click the link Reset your password :\n{reset_link}",
                from_email="rms@gmail.com",
                recipient_list=[email])
            return Response(
                {"Message" : "Password Reset lin sent Success check your Email."})
        return Response(serializer.errors)
class Reset_password(APIView):
    def post(self,request,uidb64,token):
        serializer=RestPassword(data=request.data)
        if serializer.is_valid():
            try:
                # Decode URL-encoded token
                token = unquote(token)
                uid=force_str(urlsafe_base64_decode(uidb64))
                user=User.objects.get(pk=uid)
            except Exception as e:
                return Response({
                    "Error":"Invalid user or token format"},status=status.HTTP_400_BAD_REQUEST)
            
            if not PasswordResetTokenGenerator().check_token(user,token):        
                return Response({"Error" : "Invalid or expired token"},status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data["New_password"])
            user.save()
            return Response({"Message" : "Password Changed Successfully"})
        return Response(serializer.errors)


class Change(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer= ChangePassword(data=request.data)
        if serializer.is_valid():
            user=request.user
            old_password=serializer.validated_data["Old_password"]
            new_password=serializer.validated_data["New_password"]
            confirm_password=serializer.validated_data['Confirm_password']
            if new_password != confirm_password:
                return Response({"message": "New password and confirm password do not match"},status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response(
                {"message":"Password changed succesfully"},status=status.HTTP_200_OK
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    