from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """Custom User model matching existing migrations.

    Uses an email as a unique field and includes a role.
    """

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('employee', 'Employee'),
    ]

    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    objects = CustomUserManager()


class Employee(models.Model):
    """
    Employee model linked to Django's built-in User.
    Each employee has a role: employee, hr, or manager.
    """

    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def _str_(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['user__username']