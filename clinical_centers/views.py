from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Count, Q

from .forms import CategoryForm, ClinicalCenterForm
from .models import Category, ClinicalCenter
from . import utils


MAP_DEFAULTS = {
    "lat": getattr(settings, "CLINICAL_CENTERS_DEFAULT_LAT", -17.3895),  # Cochabamba centro
    "lon": getattr(settings, "CLINICAL_CENTERS_DEFAULT_LON", -66.1568),
    "zoom": getattr(settings, "CLINICAL_CENTERS_DEFAULT_ZOOM", 13),
    "nominatim_email": getattr(settings, "CLINICAL_CENTERS_NOMINATIM_EMAIL", "contacto@example.com"),
    "auto_geolocate": getattr(settings, "CLINICAL_CENTERS_AUTO_GEOLOCATE", False),
}

TEMPLATE_ROUTE_BASE_CATEGORIES = "clinical_centers/categories/"


class CategoryListView(LoginRequiredMixin, generic.ListView):
    model = Category
    template_name = f"{TEMPLATE_ROUTE_BASE_CATEGORIES}category_list.html"
    context_object_name = "categories"
    paginate_by = 25


class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = f"{TEMPLATE_ROUTE_BASE_CATEGORIES}category_form.html"
    success_url = reverse_lazy("clinical_centers:category_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Categoría creada correctamente.")
        return response


class CategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = f"{TEMPLATE_ROUTE_BASE_CATEGORIES}category_form.html"
    success_url = reverse_lazy("clinical_centers:category_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Categoría actualizada.")
        return response


class CategoryDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Category
    template_name = f"{TEMPLATE_ROUTE_BASE_CATEGORIES}category_confirm_delete.html"
    success_url = reverse_lazy("clinical_centers:category_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Categoría eliminada.")
        return super().delete(request, *args, **kwargs)

# -------------------------------------------------------------------------
#   Clinical Centers
# -------------------------------------------------------------------------

TEMPLATE_ROUTE_BASE_CLINICAL = "clinical_centers/"

class ClinicalCenterListView(LoginRequiredMixin, generic.ListView):
    model = ClinicalCenter
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}list.html"
    context_object_name = "centers"
    paginate_by = 25


class ClinicalCenterCreateView(LoginRequiredMixin, generic.CreateView):
    model = ClinicalCenter
    form_class = ClinicalCenterForm
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}create.html"
    success_url = reverse_lazy("clinical_centers:center_list")

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault("operating_hours", utils.prepare_default_operating_hours())
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("days_of_week", utils.DAYS_OF_WEEK)
        context.setdefault("map_defaults", MAP_DEFAULTS)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Centro clínico creado correctamente.")
        return response


class ClinicalCenterUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = ClinicalCenter
    form_class = ClinicalCenterForm
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}edit.html"
    success_url = reverse_lazy("clinical_centers:center_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("days_of_week", utils.DAYS_OF_WEEK)
        context.setdefault("map_defaults", MAP_DEFAULTS)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Centro clínico actualizado.")
        return response


class ClinicalCenterDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = ClinicalCenter
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}delete.html"
    success_url = reverse_lazy("clinical_centers:center_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Centro clínico eliminado.")
        return super().delete(request, *args, **kwargs)


class ClinicalCenterDetailView(LoginRequiredMixin, generic.DetailView):
    model = ClinicalCenter
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}detail.html"
    context_object_name = "center"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        center = context["center"]

        context["services"] = utils.parse_services(center.services)
        context["operating_hours"] = utils.format_operating_hours(center.operating_hours).splitlines()
        context["is_open_now"] = utils.is_open_now(center.operating_hours)
        context["days_of_week"] = utils.DAYS_OF_WEEK
        return context


class ClinicalCenterPublicMapView(generic.TemplateView):
    template_name = f"{TEMPLATE_ROUTE_BASE_CLINICAL}map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        centers = ClinicalCenter.objects.filter(is_active=True).select_related("category")
        context["map_defaults"] = MAP_DEFAULTS
        context["centers_for_map"] = [
            {
                "id": center.pk,
                "name": center.name,
                "latitude": center.latitude,
                "longitude": center.longitude,
                "address": center.address_text or "",
                "district": center.district or "",
                "category": center.category.name if center.category else "",
                "category_id": center.category_id,
                "phone": center.phone_number or center.cell_phone_number or "",
                "email": center.email or "",
                "website": center.website or "",
                "description": center.description or "",
                "hours_note": center.hours_note or "",
                "services": utils.parse_services(center.services),
                "operating_hours": utils.format_operating_hours(center.operating_hours).splitlines(),
            }
            for center in centers
        ]
        categories_for_filter = (
            Category.objects.filter(is_active=True, centers__is_active=True)
            .annotate(active_centers=Count("centers", filter=Q(centers__is_active=True)))
            .order_by("name")
        )
        selected_category = self.request.GET.get("categoria") or ""
        context["categories_for_filter"] = categories_for_filter
        context["selected_category_id"] = str(selected_category)
        return context
