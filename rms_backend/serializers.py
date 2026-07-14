from rest_framework import serializers
from .models import User
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'phone_number',
            'first_name',
            'last_name',
            'password'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_username(self, value):
        if not value:
            return value
        if len(value) <4:
            raise serializers.ValidationError(
                "Username must be at least 4 characters."
            )

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_phone_number(self, value):
        if not value:
            return value
        if not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "Phone number already exists."
            )

        return value

    def validate_first_name(self, value):
        if not value:
            return value
        if not value.isalpha():
            raise serializers.ValidationError(
                "First name should contain only letters."
            )
        return value

    def validate_last_name(self, value):
        if not value:
            return value
        if not value.isalpha():
            raise serializers.ValidationError(
                "Last name should contain only letters."
            )
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user