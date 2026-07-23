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
