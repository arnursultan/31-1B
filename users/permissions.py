from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return (
            request.user.is_superuser
            or request.user.role == "admin"
        )


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )
