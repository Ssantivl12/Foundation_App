from django.urls import path

from . import views

app_name = "clinical_centers"

urlpatterns = [
    path("", views.ClinicalCenterListView.as_view(), name="center_list"),
    path("mapa/", views.ClinicalCenterPublicMapView.as_view(), name="center_map"),
    path("centros/nuevo/", views.ClinicalCenterCreateView.as_view(), name="center_create"),
    path("centros/<int:pk>/", views.ClinicalCenterDetailView.as_view(), name="center_detail"),
    path("centros/<int:pk>/editar/", views.ClinicalCenterUpdateView.as_view(), name="center_update"),
    path("centros/<int:pk>/eliminar/", views.ClinicalCenterDeleteView.as_view(), name="center_delete"),
    path("categorias/", views.CategoryListView.as_view(), name="category_list"),
    path("categorias/nueva/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categorias/<int:pk>/editar/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categorias/<int:pk>/eliminar/", views.CategoryDeleteView.as_view(), name="category_delete"),
]
