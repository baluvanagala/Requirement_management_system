from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "department",
        "phone",
    )

    list_filter = (
        "role",
        "department",
    )

    search_fields = (
        "user__username",
        "user__email",
        "department",
    )