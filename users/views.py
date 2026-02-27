from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views import generic

from .forms import EmailLoginForm, UserRegisterForm, SuperAdminUserCreateForm, SuperAdminUserEditForm
from .mixins import SuperuserRequiredMixin
from .models import User


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Cuenta creada exitosamente. Espera activación del administrador.")
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


class LoginView(LoginView):
    authentication_form = EmailLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def get_profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


# -------------------------------------------------------------------------
#   Gestión de usuarios (solo superadmin)
# -------------------------------------------------------------------------

TEMPLATE_ROUTE_MANAGEMENT = "users/management/"


class UserManagementListView(SuperuserRequiredMixin, generic.ListView):
    model = User
    template_name = f"{TEMPLATE_ROUTE_MANAGEMENT}user_list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).order_by("last_name", "first_name")


class UserManagementCreateView(SuperuserRequiredMixin, generic.CreateView):
    model = User
    form_class = SuperAdminUserCreateForm
    template_name = f"{TEMPLATE_ROUTE_MANAGEMENT}user_form.html"
    success_url = reverse_lazy("users:user_management_list")

    def form_valid(self, form):
        form.instance.is_superuser = False
        form.instance.is_staff = False
        response = super().form_valid(form)
        messages.success(self.request, f"Usuario {self.object.email} creado correctamente.")
        return response


class UserManagementUpdateView(SuperuserRequiredMixin, generic.UpdateView):
    model = User
    form_class = SuperAdminUserEditForm
    template_name = f"{TEMPLATE_ROUTE_MANAGEMENT}user_form.html"
    success_url = reverse_lazy("users:user_management_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_superuser:
            raise PermissionDenied("No se puede editar a un superadministrador.")
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Usuario {self.object.email} actualizado correctamente.")
        return response


class UserManagementDeleteView(SuperuserRequiredMixin, generic.DeleteView):
    model = User
    template_name = f"{TEMPLATE_ROUTE_MANAGEMENT}user_confirm_delete.html"
    success_url = reverse_lazy("users:user_management_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_superuser:
            raise PermissionDenied("No se puede eliminar a un superadministrador.")
        return obj

    def form_valid(self, form):
        email = self.get_object().email
        response = super().form_valid(form)
        messages.success(self.request, f"Usuario {email} eliminado correctamente.")
        return response
