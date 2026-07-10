from rest_framework import serializers
import re

class ForgotPassword(serializers.Serializer):
    email = serializers.EmailField()

class RestPassword(serializers.Serializer):
    New_password=serializers.CharField(min_length=8,
                                       max_length=15,
                                       write_only=True)
    Confirm_password=serializers.CharField(min_length=8,
                                       max_length=15,
                                       write_only=True)
    def validate(self,data):
        if data['New_password'] != data["Confirm_password"]:
            raise serializers.ValidationError("Password is dose not matched plase once check")
        return data


class ChangePassword(serializers.Serializer):
    Old_password=serializers.CharField(write_only=True)
    New_password=serializers.CharField(write_only=True)
    Confirm_password=serializers.CharField(write_only=True)
    def validate_New_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=!])[A-Za-z][A-Za-z\d@#$%^&+=!]{7,14}$'

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must start with a letter, contain at least one uppercase letter, one lowercase letter, one number, one special character, and be 8-15 characters long."
            )
        return value
    def validate(self,value):
        if value["New_password"] != value["Confirm_password"]:
            raise serializers.ValidationError({
                "Message" : "New password and Confirm password Not matchd plese once check"
            })
        return value