from django.urls import path

from .views import (
    LoginView, register_view, logout_view, get_profile,
    UserManagementListView, UserManagementCreateView,
    UserManagementUpdateView, UserManagementDeleteView,
)


app_name = 'users'

urlpatterns = [
    path('registro/', register_view, name='register'),
    path('inicio-sesion/', LoginView.as_view(), name='login'),
    path('cerrar-sesion/', logout_view, name='logout'),
    path('perfil/', get_profile, name='profile'),

    # Gestión de usuarios (solo superadmin)
    path('gestion/', UserManagementListView.as_view(), name='user_management_list'),
    path('gestion/crear/', UserManagementCreateView.as_view(), name='user_management_create'),
    path('gestion/<int:pk>/editar/', UserManagementUpdateView.as_view(), name='user_management_update'),
    path('gestion/<int:pk>/eliminar/', UserManagementDeleteView.as_view(), name='user_management_delete'),
]
