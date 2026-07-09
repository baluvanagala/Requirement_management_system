import re
from rest_framework import serializers

class Reset(serializers.Serializer):
    New_password = serializers.CharField(
        min_length=8,
        max_length=15
    )
    Confirm_password = serializers.CharField(
        min_length=8,
        max_length=15
    )

    def validate(self, attrs):
        password = attrs.get("New_password")
        confirm_password = attrs.get("Confirm_password")

        if (
            password != confirm_password or
            not re.match(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z][A-Za-z\d@#$%^&+=!]{7,14}$',
                password
            )
        ):
            raise serializers.ValidationError(
                "Password must match the confirm password, start with a letter, contain at least one uppercase letter, one lowercase letter, one number, one special character, and be 8-15 characters long."
            )

        return attrs