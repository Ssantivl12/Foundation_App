from __future__ import annotations

from django import forms

from .models import Category, ClinicalCenter
from . import utils


class ServicesListField(forms.Field):
    widget = forms.Textarea(attrs={"class": "js-services-textarea"})

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("help_text", "Presiona Enter o coma para agregar un servicio.")
        kwargs.setdefault("label", "Servicios ofrecidos")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return []
        return utils.parse_services(value)

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        return utils.format_services(value)


class OperatingHoursField(forms.Field):
    widget = forms.Textarea(attrs={"class": "js-hours-textarea"})

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("label", "Horarios de atención")
        kwargs.setdefault("help_text", "")
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return utils.prepare_default_operating_hours()
        try:
            return utils.parse_operating_hours(value)
        except ValueError as error:
            raise forms.ValidationError(str(error))

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        return utils.format_operating_hours(value)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ClinicalCenterForm(forms.ModelForm):
    services = ServicesListField()
    operating_hours = OperatingHoursField()

    class Meta:
        model = ClinicalCenter
        fields = [
            "name",
            "description",
            "latitude",
            "longitude",
            "address_text",
            "district",
            "phone_number",
            "cell_phone_number",
            "email",
            "website",
            "category",
            "services",
            "operating_hours",
            "hours_note",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "class": "js-latitude-input"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "class": "js-longitude-input"}),
            "address_text": forms.TextInput(attrs={"placeholder": "Calle, número, referencias", "class": "js-address-input"}),
            "district": forms.TextInput(attrs={"placeholder": "Barrio / Distrito", "class": "js-district-input"}),
            "hours_note": forms.Textarea(attrs={"rows": 2, "placeholder": "Notas breves opcionales"}),
        }
