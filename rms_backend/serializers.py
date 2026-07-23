from rest_framework import serializers
from .models import BlacklistedToken, Profile
import re
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        allowed_fields = {"email_or_phone", "password"}
        received_fields = set(self.initial_data.keys())

        extra_fields = received_fields - allowed_fields

        if extra_fields:
            raise serializers.ValidationError(
                {"extra_fields": "Enter email or either phone number "}
            )

        email_or_phone = attrs.get("email_or_phone")
        password = attrs.get("password")

        if not email_or_phone:
            raise serializers.ValidationError(
                {"email_or_phone": "Email or phone number is required."}
            )

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        user = None

        # Email Login
        if any(char.isalpha() for char in email_or_phone):

            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            if not re.match(email_pattern, email_or_phone):
                raise serializers.ValidationError(
                    {"email_or_phone": "Please enter a valid email address."}
                )

            user = User.objects.filter(email__iexact=email_or_phone).first()

            if not user:
                raise serializers.ValidationError(
                    {"email_or_phone": "Email is not registered."}
                )

        # Phone Login
        elif email_or_phone.isdigit():

            if len(email_or_phone) != 10:
                raise serializers.ValidationError(
                    {"email_or_phone": "Please enter a valid 10-digit phone number."}
                )

            user = User.objects.filter(mobile=email_or_phone).first()

            if not user:
                raise serializers.ValidationError(
                    {"email_or_phone": "Phone number is not registered."}
                )

        else:
            raise serializers.ValidationError(
                {
                    "email_or_phone": "Please enter a valid email address or phone number."
                }
            )

        if not user.is_active:
            raise serializers.ValidationError({"message": "Your account is inactive."})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid password."})

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True, allow_blank=False, trim_whitespace=True
    )

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")

        if not refresh_token:
            raise serializers.ValidationError({"refresh": "Refresh token is required."})

        try:
            token = RefreshToken(refresh_token)

        except TokenError:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token."}
            )

        if BlacklistedToken.objects.filter(token=refresh_token).exists():
            raise serializers.ValidationError(
                {"refresh": "Token is already blacklisted."}
            )

        attrs["token"] = token
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "password",
            "is_active",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "is_active", "date_joined"]

    def get_profile(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile:
            return None
        return {
            "date_of_birth": profile.date_of_birth,
            "blood_group": profile.blood_group,
            "address": profile.address,
            "profile_image": (
                profile.profile_image.url if profile.profile_image else None
            ),
        }

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters")

        if not re.match(r"^[A-Za-z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username can contain only letters, numbers and underscore."
            )
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()

    def validate_mobile(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits.")

        qs = User.objects.filter(mobile=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_password(self, value):
        if value in [None, ""]:
            return value

        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        user.is_verified = False

        if password is not None:
            user.set_password(password)

        user.save()
        Profile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance
