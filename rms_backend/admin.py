from django.contrib import admin
from .models import CustomUser, BlacklistedToken

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "mobile", "is_active")
    list_filter = ("is_active", "date_joined")
    search_fields = ("username", "email", "mobile")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "mobile")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "blacklisted_at", "expires_at")
    list_filter = ("blacklisted_at", "expires_at")
    search_fields = ("user__username", "token")
    readonly_fields = ("token", "blacklisted_at")
