from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class User(AbstractUser):

    ROLE_CHOICES = (
        ("employee", "Employee"),
        ("hr", "HR"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class Employee(models.Model):

    ROLE_CHOICES = (
        ("employee", "Employee"),
        ("hr", "HR"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee"
    )

    department = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=15, blank=True, default="")
    address = models.TextField(blank=True, default="")

    def __str__(self):
        return self.user.username



from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.user.username