"""Datos de ejemplo para probar una API a mano (archivos .http).

Son los mismos valores que usan los tests generados, así lo que se prueba a mano y lo
que prueban los tests coincide. Sirven para todas las APIs de andamio (Django, FastAPI,
Express y Next.js): todas aceptan estos valores en JSON.
"""

from __future__ import annotations

import json
from typing import Sequence

from andamio.nucleo.campos import Campo

# (al crear, al modificar)
VALORES = {
    "str": ("Texto de prueba", "Texto modificado"),
    "text": ("Descripción de prueba", "Descripción modificada"),
    "int": (1, 2),
    "decimal": (10.5, 20.75),
    "float": (1.5, 2.5),
    "bool": (True, False),
    "date": ("2025-01-15", "2025-02-20"),
    "datetime": ("2025-01-15T10:30:00Z", "2025-02-20T18:45:00Z"),
    "email": ("prueba@ejemplo.com", "modificado@ejemplo.com"),
}


def json_ejemplo(campos: Sequence[Campo], indice: int = 0, solo_el_primero: bool = False) -> str:
    """El cuerpo JSON de una petición, con un valor de ejemplo por campo."""
    elegidos = list(campos)[:1] if solo_el_primero else list(campos)
    datos = {c.nombre: VALORES[c.tipo][indice] for c in elegidos}
    return json.dumps(datos, ensure_ascii=False, indent=2)


def _login_http() -> str:
    """Lo que agrega un recurso protegido: pedir el token antes de crear, modificar o eliminar."""
    return """@usuario = admin
@clave = cambiar-esta-clave

# Este recurso está protegido (--protegido): ver es libre, pero crear, modificar y
# eliminar piden el token. Hace falta el login (python -m andamio nuevo login) y un
# usuario que exista (python manage.py createsuperuser). Ejecutá primero "Pedir el token".

### Pedir el token
# @name login
POST {{api}}/token/
Content-Type: application/json

{
  "username": "{{usuario}}",
  "password": "{{clave}}"
}

###
# REST Client toma el token de la respuesta de arriba: no hace falta copiarlo.
@token = {{login.response.body.access}}"""


def contexto_http(campos: Sequence[Campo], url_api: str, comando_api: str, protegido: bool = False) -> dict[str, str]:
    """Marcadores de la plantilla http/<plural>.http.

    url_api: la dirección base de la API (http://127.0.0.1:8000/api).
    comando_api: cómo se pone en marcha (python manage.py runserver).
    protegido: si crear, modificar y eliminar piden el token (Django con --protegido).
    """
    return {
        "url_api": url_api,
        "comando_api": comando_api,
        "http_login": _login_http() if protegido else "",
        "http_auth": "Authorization: Bearer {{token}}" if protegido else "",
        "json_crear": json_ejemplo(campos, 0),
        "json_reemplazar": json_ejemplo(campos, 1),
        "json_modificar": json_ejemplo(campos, 1, solo_el_primero=True),
    }


MARCADORES_HTTP = {
    "url_api": "dirección de la API (http/<plural>.http)",
    "comando_api": "cómo se pone en marcha la API",
    "http_login": "pedir el token antes de las peticiones (solo con --protegido)",
    "http_auth": "el encabezado con el token (solo con --protegido)",
    "json_crear": "JSON de ejemplo para crear, con todos los campos",
    "json_reemplazar": "JSON de ejemplo para reemplazar (PUT)",
    "json_modificar": "JSON de ejemplo para modificar un campo (PATCH)",
}
