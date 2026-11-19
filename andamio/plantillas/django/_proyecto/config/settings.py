"""Configuración de Django para @@proyectoTitulo@@.

Los valores que cambian entre tu PC y un servidor (clave secreta, DEBUG, base de
datos, orígenes permitidos) se leen del archivo .env, que NO se sube a git.
Si no tenés el .env, copiá .env.example con el nombre .env.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def leer_lista(nombre, defecto=""):
    """Lee una variable del .env con valores separados por coma: a,b,c -> ["a", "b", "c"]."""
    return [valor.strip() for valor in os.getenv(nombre, defecto).split(",") if valor.strip()]


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta SECRET_KEY. Copiá el archivo .env.example con el nombre .env")

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "si", "sí")

# 10.0.2.2 es tu PC vista desde el emulador de Android (para la app de React Native).
ALLOWED_HOSTS = leer_lista("ALLOWED_HOSTS", "localhost,127.0.0.1,10.0.2.2")


# --- Aplicaciones -------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

# Tus apps. andamio agrega acá cada recurso que generes.
LOCAL_APPS = [
    # --- andamio:apps (no borrar esta línea) ---
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # tiene que ir antes de CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# --- Base de datos ------------------------------------------------------------
# Por defecto usa SQLite (el archivo db.sqlite3). Para usar otra base, definí
# DATABASE_URL en el .env, por ejemplo: postgres://usuario:clave@localhost:5432/mi_base

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + (BASE_DIR / "db.sqlite3").as_posix(),
        conn_max_age=600,
    )
}


# --- Contraseñas, idioma y zona horaria ---------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Salta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- API REST (Django REST Framework) ------------------------------------------

REST_FRAMEWORK = {
    # ATENCIÓN: AllowAny deja que CUALQUIERA lea, cree, modifique y borre datos.
    # Sirve solo para desarrollar. Antes de publicar la API, agregá autenticación.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # Filtros (?campo=valor), búsqueda (?search=texto) y orden (?ordering=campo).
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Sin paginación: las listas se devuelven como un array, que es lo que esperan
    # los servicios generados para React y React Native.
    "DEFAULT_PAGINATION_CLASS": None,
    # Los decimales se envían como números (10.5) y no como texto ("10.50").
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Documentación interactiva de la API: http://127.0.0.1:8000/api/docs/
SPECTACULAR_SETTINGS = {
    "TITLE": "API de @@proyectoTitulo@@",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}


# --- CORS: qué páginas web pueden usar la API ------------------------------------
# 5173 es el puerto de Vite (React), 3000 el de Next.js y 8081 el de Expo en el navegador.
# Las apps de celular no usan CORS, así que no hace falta agregarlas.

CORS_ALLOWED_ORIGINS = leer_lista(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8081",
)
