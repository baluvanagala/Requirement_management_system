from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from rms_backend.serializers import Reset

class Forget_password(APIView):

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"message": "Email is required"}, status=HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Email not found"}, status=HTTP_404_NOT_FOUND)
        reset_link = "http://127.0.0.1:8000/api/reset_password/"
        try:
            send_mail(
                "Reset Password",
                f"Click this link to reset your password:\n{reset_link}",
                None,
                [email],
                fail_silently=False,
            )
        except Exception as exc:
            return Response(
                {"message": "Unable to send reset email", "error": str(exc)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"message": "Reset link sent successfully"}, status=HTTP_200_OK)
          


class Reset_password(APIView):
    def post(self, request):
        serializer = Reset(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['New_password']
            return Response({
                "message": "Your Password is reset successfull",
            }, status=HTTP_200_OK)
        else:
              return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

