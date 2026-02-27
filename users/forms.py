from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from .models import User, UserRole


class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "ci",
            "ci_issued_by",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "ci",
            "ci_issued_by",
        ]
        for name in required_fields:
            if name in self.fields:
                self.fields[name].required = True


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "ci",
            "ci_issued_by",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "ci",
            "ci_issued_by",
        ]
        for name in required_fields:
            if name in self.fields:
                self.fields[name].required = True


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'ci',
            'ci_issued_by',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'ci',
            'ci_issued_by',
        ]
        for name in required_fields:
            if name in self.fields:
                self.fields[name].required = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = UserRole.USER
        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))


_MANAGEABLE_ROLES = [
    (UserRole.USER, UserRole.USER.label),
    (UserRole.ADMIN, UserRole.ADMIN.label),
]

_REQUIRED_USER_FIELDS = ["email", "first_name", "last_name", "phone_number", "ci", "ci_issued_by"]


class SuperAdminUserCreateForm(UserCreationForm):
    """Formulario para que el superadmin cree usuarios con rol USER o ADMIN."""

    role = forms.TypedChoiceField(choices=_MANAGEABLE_ROLES, coerce=int, label="Rol")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email", "first_name", "last_name", "phone_number", "ci", "ci_issued_by", "role", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in _REQUIRED_USER_FIELDS:
            if name in self.fields:
                self.fields[name].required = True


class SuperAdminUserEditForm(forms.ModelForm):
    """Formulario para que el superadmin edite usuarios con rol USER o ADMIN."""

    role = forms.TypedChoiceField(choices=_MANAGEABLE_ROLES, coerce=int, label="Rol")

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone_number", "ci", "ci_issued_by", "role", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in _REQUIRED_USER_FIELDS:
            if name in self.fields:
                self.fields[name].required = True
