from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from .models import User

admin.site.site_header = "Server Admin"
admin.site.site_title = "Server Admin"
admin.site.index_title = "Management"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("email", "role", "is_staff", "is_superuser")
    ordering = ("email",)
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role & Status", {
            "fields": ("role", "is_active", "is_staff", "is_superuser")
        }),
        ("Permissions", {
            "fields": ("groups", "user_permissions")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == "admin"

    def has_view_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == "admin"

    def has_add_permission(self, request):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if obj and obj.is_superuser:
            return request.user.is_superuser
        return request.user.is_superuser or request.user.role == "admin"

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser
