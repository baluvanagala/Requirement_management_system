from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.

class CustomUser(AbstractUser):
    mobile=models.CharField(max_length=10,unique=True)
    email=models.EmailField(unique=True)

    def __str__(self):
        return self.username
    


class BlacklistedToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    token = models.TextField(unique=True)

    expires_at = models.DateTimeField()

    blacklisted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.expires_at}"