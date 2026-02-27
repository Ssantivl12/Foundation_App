from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser", "ci_issued_by")
    search_fields = ("email", "first_name", "last_name", "ci", "phone_number")

    readonly_fields = ("created_at", "last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Información personal"), {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "ci",
                "ci_issued_by",
            )
        }),
        (_("Permisos"), {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Fechas importantes"), {"fields": ("last_login", "date_joined", "created_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "phone_number",
                "ci",
                "ci_issued_by",
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
