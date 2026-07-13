from rest_framework import serializers
from .models import CustomUser,BlacklistedToken
import re
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
#################


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        allowed_fields = {"email_or_phone", "password"}
        received_fields = set(self.initial_data.keys())

        extra_fields = received_fields - allowed_fields

        if extra_fields:
            raise serializers.ValidationError(
                {
                    "extra_fields": "Enter email or either phone number "
                }
            )

        email_or_phone = attrs.get("email_or_phone")
        password = attrs.get("password")

        if not email_or_phone:
            raise serializers.ValidationError(
                {"email_or_phone": "Email or phone number is required."}
            )

        if not password:
            raise serializers.ValidationError(
                {"password": "Password is required."}
            )

        user = None

        # Email Login
        if any(char.isalpha() for char in email_or_phone):

            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            if not re.match(email_pattern, email_or_phone):
                raise serializers.ValidationError(
                    {"email_or_phone": "Please enter a valid email address."}
                )

            user = CustomUser.objects.filter(
                email__iexact=email_or_phone
            ).first()

            if not user:
                raise serializers.ValidationError(
                    {"email_or_phone": "Email is not registered."}
                )

        # Phone Login
        elif email_or_phone.isdigit():

            if len(email_or_phone) != 10:
                raise serializers.ValidationError(
                    {
                        "email_or_phone":
                        "Please enter a valid 10-digit phone number."
                    }
                )

            user = CustomUser.objects.filter(
                mobile=email_or_phone
            ).first()

            if not user:
                raise serializers.ValidationError(
                    {"email_or_phone": "Phone number is not registered."}
                )

        else:
            raise serializers.ValidationError(
                {
                    "email_or_phone":
                    "Please enter a valid email address or phone number."
                }
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"message": "Your account is inactive."}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Invalid password."}
            )

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        if not refresh_token:
            raise serializers.ValidationError(
                {"refresh": "Refresh token is required."}
            )

        try:
            token = RefreshToken(refresh_token)

        except TokenError:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token."}
            )

        # Check already blacklisted
        if BlacklistedToken.objects.filter(
            token=refresh_token
        ).exists():
            raise serializers.ValidationError(
                {"refresh": "Token is already blacklisted."}
            )

        attrs["token"] = token
        return attrs    













# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not CustomUser.objects.filter(email__iexact=value).exists():
#             raise serializers.ValidationError("Email is not registered.")
#         return value

