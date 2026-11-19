"""API de @@proyectoTitulo@@ con FastAPI.

Para ejecutarla:            python -m uvicorn app.main:app --reload
Documentación interactiva:  http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_offline import FastAPIOffline

from app.config import CORS_ALLOWED_ORIGINS
from app.db import crear_tablas
from app.errores import errores_de_validacion

# Cada recurso tiene su router. andamio agrega los import solo.
# --- andamio:imports (no borrar esta línea) ---


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    crear_tablas()  # al arrancar, crea las tablas que falten
    yield


# FastAPIOffline es FastAPI con la documentación (/docs) incluida: funciona sin internet.
app = FastAPIOffline(title="API de @@proyectoTitulo@@", lifespan=ciclo_de_vida)

# Qué páginas web pueden usar la API (React con Vite, Expo web). Se configura en el .env.
app.add_middleware(CORSMiddleware, allow_origins=CORS_ALLOWED_ORIGINS, allow_methods=["*"], allow_headers=["*"])

# Errores de validación con el mismo formato que Django REST Framework:
# 400 con {"campo": ["mensaje"]}. Así los servicios de React y React Native funcionan igual.
app.add_exception_handler(RequestValidationError, errores_de_validacion)

# Rutas de cada recurso (andamio agrega una línea por cada uno):
# --- andamio:routers (no borrar esta línea) ---


@app.get("/api/", include_in_schema=False)
def inicio():
    """/api/ lleva a la documentación."""
    return RedirectResponse("/docs")
