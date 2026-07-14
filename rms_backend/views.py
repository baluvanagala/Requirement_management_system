from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()
class ForgotPassword(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error":"User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://127.0.0.1:8000/api/reset-password/{uid}/{token}/"
        send_mail(
            subject="Reset Password",
            message=f"Click the link below:\n\n{reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response(
            {"message":"Reset link sent successfully"}
        )
    
    
class ResetPassword(APIView):
    def post(self, request, uidb64, token):
        password = request.data.get("New_password")
        confirm_password = request.data.get("confirm_password")
        if password != confirm_password:
            return Response(
                {"error":"Passwords do not match"},
                status=400
            )
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response(
                {"error":"Invalid user"},
                status=400
            )
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error":"Invalid Token"},
                status=400
            )
        user.set_password(password)
        user.save()
        return Response(
            {"message":"Password Reset Successfully"}
        )