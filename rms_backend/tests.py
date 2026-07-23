from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import User

<<<<<<< HEAD
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
=======

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RegistrationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration_sends_otp_and_creates_pending_user(self):
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone_number': '1234567890',
            'password': 'StrongPass123',
            'date_of_birth': '1990-01-01',
            'gender': 'male',
        }

        response = self.client.post('/api/register/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], 'john@example.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('OTP', mail.outbox[0].subject)

        user = User.objects.get(email='john@example.com')
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_active)
        self.assertEqual(len(user.otp), 6)

    def test_registration_accepts_minimal_payload(self):
        payload = {
            'email': 'minimal@example.com',
            'password': 'StrongPass123',
        }

        response = self.client.post('/api/register/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], 'minimal@example.com')
        user = User.objects.get(email='minimal@example.com')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')

    def test_otp_verification_marks_user_verified(self):
        user = User.objects.create_user(
            email='verified@example.com',
            password='StrongPass123',
            first_name='Verified',
            last_name='User',
            otp='123456',
            is_verified=False,
            is_active=False,
        )

        response = self.client.post('/api/verify-otp/', {'email': user.email, 'otp': '123456'}, format='json')

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)

    def test_login_with_email_or_phone_number(self):
        user = User.objects.create_user(
            email='login@example.com',
            password='StrongPass123',
            first_name='Login',
            last_name='User',
            phone_number='5551234567',
            is_verified=True,
            is_active=True,
        )

        email_response = self.client.post('/api/login/', {'identifier': 'login@example.com', 'password': 'StrongPass123'}, format='json')
        self.assertEqual(email_response.status_code, 200)
        self.assertEqual(email_response.data['email'], 'login@example.com')

        phone_response = self.client.post('/api/login/', {'identifier': '5551234567', 'password': 'StrongPass123'}, format='json')
        self.assertEqual(phone_response.status_code, 200)
        self.assertEqual(phone_response.data['email'], 'login@example.com')
>>>>>>> register_api
