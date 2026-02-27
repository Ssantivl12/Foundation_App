# Foundation App - Project Memory

## Stack
- Django 5.x + PostgreSQL
- Auth: Custom `User` model (`users.User`) extendiendo `AbstractUser`, login por email
- Templates: server-side, directorio `templates/` en raíz (no en apps)
- Static: directorio `static/` en raíz

## Roles de usuario
- `UserRole.USER = 0` — usuario base
- `UserRole.ADMIN_STAFF = 1` — personal administrativo
- `UserRole.ADMIN = 2` — administrador
- Superadmin: `is_superuser=True` (Django nativo, sin rol especial en `UserRole`)

## Módulos/Apps
- `users/` — autenticación, perfiles, CRUD de gestión de usuarios
- `clinical_centers/` — centros clínicos y categorías
- `foundation_core/` — settings, urls raíz, vistas home y admin panel

## Arquitectura de vistas
- CBVs de `django.views.generic` con mixins de permisos propios en `users/mixins.py`
- NO se usa el patrón Repository — ORM directo en vistas
- Patrón de templates: `shared/base.html` > `shared/base_form.html` / `shared/base_confirm.html`
- `shared/form_fields.html` renderiza todos los campos del form con labels y errores

## Mixins de permisos (`users/mixins.py`)
- `LoginRequiredMixin` — requiere autenticación, redirige a `users:login`
- `AdminStaffRoleRequiredMixin` — requiere rol ADMIN_STAFF o ADMIN
- `AdminRoleRequiredMixin` — requiere rol ADMIN
- `SuperuserRequiredMixin` — requiere `is_superuser=True`

## CRUD de gestión de usuarios (`/usuarios/gestion/`)
- Solo accesible por superadmins (`SuperuserRequiredMixin`)
- Roles creables/editables: solo USER y ADMIN (no ADMIN_STAFF, no superuser)
- Queryset excluye `is_superuser=True` — protección doble en get_object() también
- `SuperAdminUserCreateForm` — hereda `UserCreationForm`, incluye password1/password2
- `SuperAdminUserEditForm` — `ModelForm` sin contraseña
- Templates en `templates/users/management/`
- URLs: `user_management_list`, `user_management_create`, `user_management_update`, `user_management_delete`

## URLs raíz
- `/` — home
- `/admin/` — Django admin
- `/panel-administrador/` — admin panel custom
- `/usuarios/` — include `users.urls`
- `/centros-clinicos/` — include `clinical_centers.urls`

## Convenciones
- Mensajes de éxito/error con `django.contrib.messages`
- Idioma español en labels, mensajes y URLs
- `paginate_by = 25` en ListViews
