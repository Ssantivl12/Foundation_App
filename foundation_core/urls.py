from django.contrib import admin
from django.urls import path, include

from .views import HomeView, AdminPanelView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path('panel-administrador/', AdminPanelView.as_view(), name="admin-panel"),

    path('usuarios/', include('users.urls')),
    
    path('centros-clinicos/', include('clinical_centers.urls')),
]
