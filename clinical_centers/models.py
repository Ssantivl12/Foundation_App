from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class Category(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(models.functions.Lower("name"), name="uniq_category_name_lower")
        ]

    def __str__(self):
        return self.name


class ClinicalCenter(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    address_text = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=50, blank=True)

    # Contacto
    phone_number = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r"^[0-9+\-\s()]{6,}$", "Teléfono inválido.")]
    )
    cell_phone_number = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r"^[0-9+\-\s()]{6,}$", "Celular inválido.")]
    )
    email = models.EmailField(max_length=120, blank=True)
    website = models.URLField(blank=True)

    # Clasificación
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="centers"
    )

    # --- Campos simplificados (JSON) ---
    # Lista de servicios simples (strings). Ej: ["Vacunación","Control neonatal","Consejería"]
    services = models.JSONField(default=list, blank=True, help_text="Lista de servicios (strings).")

    # Horarios por día (0=Lunes .. 6=Domingo). Cada día es lista de tramos {open, close}.
    # Ej: {"0":[{"open":"08:00","close":"12:00"},{"open":"14:00","close":"18:00"}], "6":[]}
    operating_hours = models.JSONField(default=dict, blank=True, help_text=(
        "JSON por día: 0=Lun..6=Dom. Ej: "
        '{"0":[{"open":"08:00","close":"12:00"}], "1":[{"open":"08:00","close":"16:00"}], "6":[]}'
    ))

    # Nota corta opcional para mostrar en la ficha (p.ej. “Solo con referencia médica”)
    hours_note = models.CharField(max_length=160, blank=True)

    # Estado / auditoría
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Centro Clínico"
        verbose_name_plural = "Centros Clínicos"
        ordering = ("name",)
        indexes = [
            models.Index(fields=("is_active",)),
            models.Index(fields=("latitude", "longitude")),
        ]

    def __str__(self):
        return self.name
