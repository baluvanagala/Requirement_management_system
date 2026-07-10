from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rms_backend.models import Employee

User = get_user_model()


class PermissionTests(APITestCase):

    def setUp(self):
        # Create HR user
        self.hr_user = User.objects.create_user(
            username='hr_user',
            email='hr@example.com',
            password='password123',
            role='hr',
        )
        self.hr_employee = Employee.objects.create(
            user=self.hr_user,
            role='hr',
            department='HR',
        )

        # Create Manager user
        self.manager_user = User.objects.create_user(
            username='manager_user',
            email='manager@example.com',
            password='password123',
            role='manager',
        )
        self.manager_employee = Employee.objects.create(
            user=self.manager_user,
            role='manager',
            department='Management',
        )

        # Create regular Employee user
        self.employee_user = User.objects.create_user(
            username='employee_user',
            email='employee@example.com',
            password='password123',
            role='employee',
        )
        self.employee_profile = Employee.objects.create(
            user=self.employee_user,
            role='employee',
            department='Engineering',
        )

        self.register_url = reverse('register')
        self.employee_list_url = reverse('employee-list')

    # ─── Registration Tests ───────────────────────────────────────────

    def test_anonymous_registration_is_blocked(self):
        data = {
            "username": "new_emp",
            "password": "password123",
            "email": "new_emp@example.com",
            "role": "employee",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_employee_registration_is_blocked(self):
        self.client.force_authenticate(user=self.employee_user)
        data = {
            "username": "new_emp",
            "password": "password123",
            "email": "new_emp@example.com",
            "role": "employee",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_can_register_new_user(self):
        self.client.force_authenticate(user=self.hr_user)
        data = {
            "username": "new_emp",
            "password": "password123",
            "email": "new_emp@example.com",
            "role": "employee",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'new_emp')

    def test_manager_can_register_new_user(self):
        self.client.force_authenticate(user=self.manager_user)
        data = {
            "username": "new_emp2",
            "password": "password123",
            "email": "new_emp2@example.com",
            "role": "employee",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'new_emp2')

    # ─── Employee List GET Tests ──────────────────────────────────────

    def test_anonymous_cannot_get_employee_list(self):
        response = self.client.get(self.employee_list_url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_employee_cannot_get_employee_list(self):
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.employee_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_can_get_employee_list(self):
        self.client.force_authenticate(user=self.hr_user)
        response = self.client.get(self.employee_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return list of all employees
        self.assertGreaterEqual(len(response.data), 3)

    def test_manager_can_get_employee_list(self):
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.employee_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    # ─── Employee List POST (Credentials Body) Tests ──────────────────

    def test_post_employee_list_with_hr_credentials_succeeds(self):
        # Unauthenticated client calling POST with credentials in body.
        # authenticate() uses USERNAME_FIELD which is email for our User model.
        data = {
            "username": "hr@example.com",
            "password": "password123",
        }
        response = self.client.post(self.employee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 3)

    def test_post_employee_list_with_employee_credentials_fails(self):
        data = {
            "username": "employee@example.com",
            "password": "password123",
        }
        response = self.client.post(self.employee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_employee_list_with_invalid_credentials_fails(self):
        data = {
            "username": "hr@example.com",
            "password": "wrong_password",
        }
        response = self.client.post(self.employee_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
