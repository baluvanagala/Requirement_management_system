from django.test import TestCase

from .models import CustomUser
from .serializers import LoginSerializer, UserSerializer


class CustomUserSerializerTests(TestCase):
    def test_login_serializer_accepts_custom_user_credentials(self):
        user = CustomUser.objects.create_user(
            username='jane',
            email='jane@example.com',
            mobile='9876543210',
            password='StrongPass123',
        )

        serializer = LoginSerializer(
            data={
                'email_or_phone': user.email,
                'password': 'StrongPass123',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['user'], user)

    def test_user_serializer_creates_custom_user_with_mobile(self):
        serializer = UserSerializer(
            data={
                'username': 'alex',
                'email': 'alex@example.com',
                'mobile': '1234567890',
                'password': 'StrongPass123',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertIsInstance(user, CustomUser)
        self.assertEqual(user.mobile, '1234567890')
        self.assertTrue(user.check_password('StrongPass123'))
