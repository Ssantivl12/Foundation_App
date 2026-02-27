# Foundation App

Aplicación Django con autenticación por email y gestión de centros clínicos. Renderiza templates (no DRF) y expone un mapa público de centros activos.

## Componentes principales
- `foundation_core`: home y panel administrativo base.
- `users`: registro, login/logout y perfil de usuario (modelo personalizado).
- `clinical_centers`: CRUD de centros y categorías, mapa público filtrable.
- Documentación de rutas HTML: `static/docs/openapi.yaml`.

## Requisitos
- Python 3.12+ (recomendado para Django 5.2)
- PostgreSQL 14+ accesible
- Virtualenv (`python -m venv`) o similar

## Configuración rápida
1) Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2) Configurar variables de entorno (usa `python-decouple`). Crea un `.env` en la raíz:
   ```
   DJANGO_SECRET_KEY=pon-una-clave-segura
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   DB_NAME=foundation
   DB_USER=foundation
   DB_PASSWORD=foundation
   DB_HOST=localhost
   DB_PORT=5432
   ```
3) Preparar base de datos y usuario en PostgreSQL según los valores anteriores.
4) Migraciones y usuario admin:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5) Servir en local:
   ```bash
   python manage.py runserver
   ```
   La app servirá el home en `http://localhost:8000/` y el admin nativo en `/admin/`.

## Documentación de rutas HTML (OpenAPI)
- Archivo: `static/docs/openapi.yaml`.
- Con el servidor en `runserver`, se puede acceder directo a `http://localhost:8000/static/docs/openapi.yaml`.

### Ver en Swagger Editor (UI web rápida)
1) Abre https://editor.swagger.io/.
2) `File -> Import URL` y pega `http://localhost:8000/static/docs/openapi.yaml` (o carga el archivo desde disco).
3) Se renderizarán las vistas HTML, métodos y redirecciones documentadas.

## Producción (resumen)
- Configura `DJANGO_DEBUG=False` y `DJANGO_ALLOWED_HOSTS` apropiados.
- Ejecuta `python manage.py collectstatic` hacia el `STATIC_ROOT`.
- Usa un servidor WSGI (gunicorn/uwsgi) detrás de Nginx y apunta a PostgreSQL gestionado.
