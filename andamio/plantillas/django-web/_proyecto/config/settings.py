"""Configuración de Django para @@proyectoTitulo@@ (sitio web con plantillas HTML).

Los valores que cambian entre tu PC y un servidor (clave secreta, DEBUG, base de
datos) se leen del archivo .env, que NO se sube a git.
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

ALLOWED_HOSTS = leer_lista("ALLOWED_HOSTS", "localhost,127.0.0.1")


# --- Aplicaciones -------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Tus apps. andamio agrega acá cada crud que generes.
LOCAL_APPS = [
    # --- andamio:apps (no borrar esta línea) ---
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# Plantillas HTML: las del proyecto (templates/: base.html, inicio.html, login...) y las
# de cada app (<app>/templates/<app>/...), que encuentra solo gracias a APP_DIRS.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Archivos estáticos (CSS, imágenes, JavaScript) ------------------------------
# En las plantillas: {% load static %} y <link href="{% static 'css/estilos.css' %}">

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # python manage.py collectstatic (para publicar)


# --- Login ----------------------------------------------------------------------
# Las vistas con LoginRequiredMixin (los crud generados con --protegido) mandan acá
# a quien no inició sesión. Después de entrar o salir, se vuelve al inicio.

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "inicio"
