from rest_framework.permissions import BasePermission


class IsHRorAdmin(BasePermission):
    """Allow access to users with role hr, manager, or admin."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("hr", "manager", "admin")
        )


class IsAdmin(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )