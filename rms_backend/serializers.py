import re
from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    New_password = serializers.CharField(
        min_length=8,
        max_length=15,
        write_only=True
    )
    confirm_password = serializers.CharField(
        write_only=True
    )

    def validate_New_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Z][A-Za-z\d@#$%^&+=!]{7,14}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "plase enter the 'Abcd@123' this type of password enter the this type of minimum_length 8 "
            )

        return value

    def validate(self, attrs):
        if attrs["New_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return attrs