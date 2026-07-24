from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    """
    Custom user model.

    Extends Django's AbstractUser model by adding
    a unique mobile number and email address for
    user authentication and identification.
    """

    mobile = models.CharField(
        max_length=10, unique=True, verbose_name="Mobile Number", db_column="mobile"
    )
    email = models.EmailField(
        unique=True, verbose_name="Email Address", db_column="email"
    )
    

    def __str__(self):
        return self.username


class BlacklistedToken(models.Model):
    """
    Stores blacklisted JWT refresh tokens.

    Used during logout to invalidate refresh
    tokens and prevent them from being used
    again for generating new access tokens.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User",
        db_column="user_id",
    )

    token = models.TextField(
        unique=True, verbose_name="Refresh Token", db_column="token"
    )

    expires_at = models.DateTimeField(verbose_name="Expires At", db_column="expires_at")

    blacklisted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Blacklisted At", db_column="blacklisted_at"
    )

    def __str__(self):
        return f"{self.user} - {self.expires_at}"


class Profile(models.Model):
    """
    Stores additional profile information
    associated with a user account.

    Contains personal details such as date
    of birth, blood group, address, and
    profile image.
    """

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User",
        db_column="user_id",
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name="Date of Birth", db_column="date_of_birth"
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        null=True,
        blank=True,
        verbose_name="Blood Group",
        db_column="blood_group",
    )
    address = models.TextField(
        null=True, blank=True, verbose_name="Address", db_column="address"
    )
    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True,
        verbose_name="Profile Image",
        db_column="profile_image",
    )

    def __str__(self):
        return f"{self.user.username} Profile"
    
# import random

# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# import uuid


# class CustomUserManager(BaseUserManager):

#     def create_user(self, email, username=None, phone_number=None, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email is required")

#         email = self.normalize_email(email)

#         user = self.model(
#             email=email,
#             username=username,
#             phone_number=phone_number,
#             **extra_fields
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, username, phone_number, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         return self.create_user(
#             email,
#             username,
#             phone_number,
#             password,
#             **extra_fields
#         )


# class User(AbstractBaseUser, PermissionsMixin):
#     user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=50, unique=True, null=True, blank=True)
#     phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

#     first_name = models.CharField(max_length=50, blank=True, default='')
#     last_name = models.CharField(max_length=50, blank=True, default='')

#     email_verified = models.BooleanField(default=False)
#     phone_verified = models.BooleanField(default=False)
#     is_verified = models.BooleanField(default=False)

#     otp = models.CharField(max_length=6, blank=True, null=True)

#     is_active = models.BooleanField(default=False)
#     is_staff = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = "email"

#     REQUIRED_FIELDS = [
#         "username",
#         "phone_number",
#     ]

#     def __str__(self):
#         return self.email

