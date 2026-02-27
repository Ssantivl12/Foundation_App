from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import UserRole


class LoginRequiredMixin(AccessMixin):
    login_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class AdminStaffRoleRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in {UserRole.ADMIN_STAFF, UserRole.ADMIN}:
            raise PermissionDenied("Acceso restringido a personal administrativo.")
        return super().dispatch(request, *args, **kwargs)


class AdminRoleRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != UserRole.ADMIN:
            raise PermissionDenied("Acceso restringido a administradores.")
        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            raise PermissionDenied("Acceso restringido a superadministradores.")
        return super().dispatch(request, *args, **kwargs)
