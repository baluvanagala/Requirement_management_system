from rest_framework import serializers
from .models import CustomUser
from django.db.models import Q


class LoginSerializer(serializers.Serializer):
    email_or_phone=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, attrs):
        email_or_phone=attrs.get('email_or_phone')
        password=attrs.get('password')

        if not email_or_phone:
            raise serializers.ValidationError(
                {'email_or_phone':'Email or Password  is required.'}
            )
        if not password:
            raise serializers.ValidationError(
                {'email_or_phone': 'Password is required'}
            )
        
        user = CustomUser.objects.filter(
            Q(email=email_or_phone) |
            Q(mobile=email_or_phone)
        ).first()

        if not user:
            raise serializers.ValidationError(
                {"email_or_phone": "User not found."}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {'message':'Your account  is inactivated'}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Invalid password."}
            )

        attrs['user'] = user
        return attrs