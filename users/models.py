from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.functions import Lower


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", None)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuario debe tener is_superuser=True.")

        required_fields = ["first_name", "last_name", "phone_number", "ci", "ci_issued_by"]
        missing = [f for f in required_fields if extra_fields.get(f) is None or (isinstance(extra_fields.get(f), str) and not extra_fields.get(f).strip())]
        if missing:
            raise ValueError(
                f"Faltan campos obligatorios para superusuario: {', '.join(missing)}"
            )

        return self.create_user(email, password, **extra_fields)


class UserRole(models.IntegerChoices):
    USER = 0, "User"
    ADMIN_STAFF = 1, "Administration_Staff"
    ADMIN = 2, "Administrator"


class CiIssuedBy(models.IntegerChoices):
    CB = 0, "Cochabamba"
    LP = 1, "La Paz"
    OR = 2, "Oruro"
    PO = 3, "Potosí"
    CH = 4, "Chuquisaca"
    PA = 5, "Pando"
    BE = 6, "Beni"
    SC = 7, "Santa Cruz"


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)

    email = models.EmailField(
        max_length=100,
        unique=True,
        validators=[EmailValidator(message="El formato del correo electrónico no es válido.")],
    )

    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    ci = models.CharField(max_length=15, null=False, blank=True)
    ci_issued_by = models.PositiveSmallIntegerField(choices=CiIssuedBy, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=False, blank=True)

    role = models.PositiveSmallIntegerField(choices=UserRole.choices, default=UserRole.USER)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "ci", "ci_issued_by"]

    def __str__(self):
        return self.email

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="uniq_user_email_lower",
            )
        ]
