"""
Comando de seed para poblar la base de datos con datos de prueba.

Uso:
    python manage.py seed              # crea datos si no existen
    python manage.py seed --reset      # borra datos de seed y los recrea
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from clinical_centers.models import Category, ClinicalCenter
from users.models import CiIssuedBy, User, UserRole

PASSWORD = "passwd12345"

# ---------------------------------------------------------------------------
# Datos de usuarios
# ---------------------------------------------------------------------------

SEED_USERS = [
    {
        "email": "superadmin@gmail.com",
        "first_name": "Super",
        "last_name": "Administrador",
        "phone_number": "77700001",
        "ci": "10000001",
        "ci_issued_by": CiIssuedBy.CB,
        "is_superuser": True,
        "is_staff": True,
        "is_active": True,
        "role": UserRole.ADMIN,
    },
    {
        "email": "admin@gmail.com",
        "first_name": "Ana",
        "last_name": "Rodríguez",
        "phone_number": "77700002",
        "ci": "10000002",
        "ci_issued_by": CiIssuedBy.LP,
        "role": UserRole.ADMIN,
        "is_active": True,
    },
    {
        "email": "staff@gmail.com",
        "first_name": "Carlos",
        "last_name": "Mendoza",
        "phone_number": "77700003",
        "ci": "10000003",
        "ci_issued_by": CiIssuedBy.CB,
        "role": UserRole.ADMIN_STAFF,
        "is_active": True,
    },
    {
        "email": "usuario@gmail.com",
        "first_name": "María",
        "last_name": "López",
        "phone_number": "77700004",
        "ci": "10000004",
        "ci_issued_by": CiIssuedBy.SC,
        "role": UserRole.USER,
        "is_active": True,
    },
    {
        "email": "inactivo@gmail.com",
        "first_name": "Pedro",
        "last_name": "Vargas",
        "phone_number": "77700005",
        "ci": "10000005",
        "ci_issued_by": CiIssuedBy.CB,
        "role": UserRole.USER,
        "is_active": False,
    },
]

# ---------------------------------------------------------------------------
# Datos de categorías
# ---------------------------------------------------------------------------

SEED_CATEGORIES = [
    {"name": "Centro de Salud", "description": "Establecimientos de atención primaria de salud.", "is_active": True},
    {"name": "Policlínica", "description": "Unidades con múltiples especialidades médicas.", "is_active": True},
    {"name": "Hospital", "description": "Centros hospitalarios de referencia.", "is_active": True},
    {"name": "Clínica Especializada", "description": "Atención especializada en una rama médica.", "is_active": True},
    {"name": "Centro de Rehabilitación", "description": "Servicios de fisioterapia y recuperación.", "is_active": True},
    {"name": "Laboratorio Clínico", "description": "Análisis de laboratorio y diagnóstico.", "is_active": False},
]

# ---------------------------------------------------------------------------
# Horarios reutilizables
# ---------------------------------------------------------------------------

_HORAS_LAB = [{"open": "08:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}]
_HORAS_MAÑANA = [{"open": "08:00", "close": "13:00"}]
_HORAS_COMPLETO = [{"open": "07:00", "close": "19:00"}]
_HORAS_24H = [{"open": "00:00", "close": "23:59"}]


def _horario(lun=None, mar=None, mie=None, jue=None, vie=None, sab=None, dom=None):
    return {
        "0": lun or [],
        "1": mar or [],
        "2": mie or [],
        "3": jue or [],
        "4": vie or [],
        "5": sab or [],
        "6": dom or [],
    }


# ---------------------------------------------------------------------------
# Datos de centros clínicos
# ---------------------------------------------------------------------------

SEED_CENTERS = [
    {
        "name": "Centro de Salud Villa Pagador",
        "category_name": "Centro de Salud",
        "description": "Centro de atención primaria que brinda consultas generales, control prenatal y vacunación.",
        "latitude": -17.4200,
        "longitude": -66.1400,
        "address_text": "Av. Circunvalación esq. Calle 3, Villa Pagador",
        "district": "Cercado",
        "phone_number": "4-252100",
        "cell_phone_number": "76601001",
        "email": "cpagador@salud.gob.bo",
        "services": ["Consulta general", "Control prenatal", "Vacunación", "Odontología"],
        "operating_hours": _horario(
            lun=_HORAS_LAB, mar=_HORAS_LAB, mie=_HORAS_LAB,
            jue=_HORAS_LAB, vie=_HORAS_LAB, sab=_HORAS_MAÑANA,
        ),
        "is_active": True,
    },
    {
        "name": "Policlínica Miraflores",
        "category_name": "Policlínica",
        "description": "Unidad polivalente con especialidades en medicina interna, pediatría y ginecología.",
        "latitude": -17.3800,
        "longitude": -66.1600,
        "address_text": "Calle Sucre N° 450, Miraflores",
        "district": "Cercado",
        "phone_number": "4-425600",
        "cell_phone_number": "76601002",
        "email": "miraflores@clinica.bo",
        "website": "https://example.com/miraflores",
        "services": ["Medicina interna", "Pediatría", "Ginecología", "Nutrición", "Psicología"],
        "operating_hours": _horario(
            lun=_HORAS_LAB, mar=_HORAS_LAB, mie=_HORAS_LAB,
            jue=_HORAS_LAB, vie=_HORAS_LAB,
        ),
        "hours_note": "Sábados solo con cita previa.",
        "is_active": True,
    },
    {
        "name": "Hospital Viedma",
        "category_name": "Hospital",
        "description": "Hospital público de referencia departamental con urgencias las 24 horas.",
        "latitude": -17.3950,
        "longitude": -66.1570,
        "address_text": "Av. Aniceto Arce s/n, Centro",
        "district": "Cercado",
        "phone_number": "4-254200",
        "email": "viedma@salud.gob.bo",
        "services": ["Urgencias", "Cirugía", "Traumatología", "Cardiología", "Neonatología", "UCI"],
        "operating_hours": _horario(
            lun=_HORAS_24H, mar=_HORAS_24H, mie=_HORAS_24H,
            jue=_HORAS_24H, vie=_HORAS_24H, sab=_HORAS_24H, dom=_HORAS_24H,
        ),
        "hours_note": "Urgencias disponible las 24 h.",
        "is_active": True,
    },
    {
        "name": "Clínica Especializada del Sur",
        "category_name": "Clínica Especializada",
        "description": "Centro privado especializado en dermatología y cirugía estética.",
        "latitude": -17.4350,
        "longitude": -66.1650,
        "address_text": "Av. Blanco Galindo Km 5, Quillacollo",
        "district": "Quillacollo",
        "phone_number": "4-491000",
        "cell_phone_number": "76601004",
        "email": "sur@clinicaspecializada.bo",
        "services": ["Dermatología", "Cirugía estética", "Láser terapéutico"],
        "operating_hours": _horario(
            lun=_HORAS_COMPLETO, mar=_HORAS_COMPLETO, mie=_HORAS_COMPLETO,
            jue=_HORAS_COMPLETO, vie=_HORAS_COMPLETO, sab=_HORAS_MAÑANA,
        ),
        "is_active": True,
    },
    {
        "name": "Centro de Rehabilitación Vida Plena",
        "category_name": "Centro de Rehabilitación",
        "description": "Fisioterapia, kinesiología y rehabilitación neurológica para todas las edades.",
        "latitude": -17.3750,
        "longitude": -66.1480,
        "address_text": "Calle Colombia N° 120, Recoleta",
        "district": "Cercado",
        "cell_phone_number": "76601005",
        "email": "vidaplena@rehab.bo",
        "services": ["Fisioterapia", "Kinesiología", "Rehabilitación neurológica", "Terapia ocupacional"],
        "operating_hours": _horario(
            lun=_HORAS_LAB, mar=_HORAS_LAB, mie=_HORAS_LAB,
            jue=_HORAS_LAB, vie=_HORAS_LAB,
        ),
        "is_active": True,
    },
    {
        "name": "Centro de Salud Temporal (inactivo)",
        "category_name": "Centro de Salud",
        "description": "Centro en proceso de habilitación, aún fuera de servicio.",
        "latitude": -17.4100,
        "longitude": -66.1300,
        "address_text": "Calle Nueva s/n, Sacaba",
        "district": "Sacaba",
        "phone_number": "4-280000",
        "services": [],
        "operating_hours": _horario(),
        "is_active": False,
    },
]


# ---------------------------------------------------------------------------
# Comando
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina los datos de seed existentes antes de recrearlos.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        with transaction.atomic():
            self._seed_users()
            categories = self._seed_categories()
            self._seed_centers(categories)

        self.stdout.write(self.style.SUCCESS("\nSeed completado exitosamente."))

    # ------------------------------------------------------------------

    def _reset(self):
        self.stdout.write("Eliminando datos de seed anteriores...")
        emails = [u["email"] for u in SEED_USERS]
        deleted_users, _ = User.objects.filter(email__in=emails).delete()

        center_names = [c["name"] for c in SEED_CENTERS]
        deleted_centers, _ = ClinicalCenter.objects.filter(name__in=center_names).delete()

        category_names = [c["name"] for c in SEED_CATEGORIES]
        deleted_categories, _ = Category.objects.filter(name__in=category_names).delete()

        self.stdout.write(
            f"  Eliminados: {deleted_users} usuarios, "
            f"{deleted_centers} centros, {deleted_categories} categorías."
        )

    def _seed_users(self):
        self.stdout.write("\nCreando usuarios...")
        for data in SEED_USERS:
            email = data["email"]
            is_superuser = data.get("is_superuser", False)

            defaults = {k: v for k, v in data.items() if k != "email"}

            user, created = User.objects.update_or_create(email=email, defaults=defaults)
            user.set_password(PASSWORD)
            user.save(update_fields=["password"])

            label = "creado" if created else "actualizado"
            role_label = "superadmin" if is_superuser else user.get_role_display()
            self.stdout.write(f"  [{label}] {email} — {role_label}")

    def _seed_categories(self):
        self.stdout.write("\nCreando categorías...")
        categories = {}
        for data in SEED_CATEGORIES:
            name = data["name"]
            obj, created = Category.objects.update_or_create(
                name=name,
                defaults={"description": data["description"], "is_active": data["is_active"]},
            )
            categories[name] = obj
            label = "creada" if created else "actualizada"
            self.stdout.write(f"  [{label}] {name}")
        return categories

    def _seed_centers(self, categories):
        self.stdout.write("\nCreando centros clínicos...")
        for data in SEED_CENTERS:
            category_name = data.pop("category_name")
            name = data["name"]

            data["category"] = categories.get(category_name)

            obj, created = ClinicalCenter.objects.update_or_create(
                name=name,
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            label = "creado" if created else "actualizado"
            active = "activo" if obj.is_active else "inactivo"
            self.stdout.write(f"  [{label}] {name} ({active})")
