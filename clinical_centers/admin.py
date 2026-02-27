from django.contrib import admin

from . import utils
from .forms import CategoryForm, ClinicalCenterForm
from .models import Category, ClinicalCenter


@admin.register(ClinicalCenter)
class ClinicalCenterAdmin(admin.ModelAdmin):
    form = ClinicalCenterForm
    list_display = (
        "name",
        "category",
        "district",
        "phone_number",
        "is_active",
        "created_at",
        "services_preview",
    )
    list_filter = ("is_active", "category", "district")
    search_fields = ("name", "address_text", "district", "phone_number", "email")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Información General", {
            "fields": ("name", "description", "category", "is_active"),
        }),
        ("Ubicación", {
            "fields": ("latitude", "longitude", "address_text", "district"),
        }),
        ("Contacto", {
            "fields": ("phone_number", "cell_phone_number", "email", "website"),
        }),
        ("Servicios y Horarios", {
            "fields": ("services", "operating_hours", "hours_note"),
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def services_preview(self, obj: ClinicalCenter) -> str:
        services = utils.parse_services(obj.services)
        if not services:
            return "—"
        preview = ", ".join(services[:3])
        if len(services) > 3:
            preview = f"{preview}…"
        return preview

    services_preview.short_description = "Servicios"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ("name", "is_active")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("is_active",)
