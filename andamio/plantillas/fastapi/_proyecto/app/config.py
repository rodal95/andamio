"""Configuración del proyecto, leída del archivo .env (como settings.py en Django)."""

import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def leer_lista(nombre, defecto=""):
    """Lee una variable del .env con valores separados por coma: a,b,c -> ["a", "b", "c"]."""
    return [valor.strip() for valor in os.getenv(nombre, defecto).split(",") if valor.strip()]


# Base de datos: por defecto, el archivo datos.db. Para usar otra, definí DATABASE_URL en el .env.
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///" + (RAIZ / "datos.db").as_posix()

# Páginas web que pueden usar la API (React con Vite, Next.js, Expo web).
CORS_ALLOWED_ORIGINS = leer_lista(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8081"
)

# Zona horaria de las fechas con hora (igual que TIME_ZONE en Django).
ZONA_HORARIA = ZoneInfo(os.getenv("ZONA_HORARIA") or "America/Argentina/Salta")
