# guía: Lo delicado del login: cómo se guardan las contraseñas y cómo se arman y se leen los tokens.
"""Contraseñas (hash con PBKDF2, como Django) y tokens JWT (como SimpleJWT).

- La contraseña nunca se guarda: se guarda un hash con "sal" (un valor al azar por usuario).
  Para comprobarla, se calcula el hash de lo que escribió la persona y se compara.
- El token de acceso dura poco (60 minutos); el de refresco sirve para pedir otro sin volver
  a escribir la contraseña (7 días). Los dos van firmados con SECRET_KEY (el .env): si
  alguien cambia una letra del token, la firma ya no coincide y la API lo rechaza.
"""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import SECRET_KEY
from app.db import Sesion

from .modelo import Usuario

ITERACIONES = 600_000  # las que recomienda OWASP para PBKDF2-SHA256
DURACION_ACCESO = timedelta(minutes=60)
DURACION_REFRESCO = timedelta(days=7)


def hash_de(password: str, sal: bytes | None = None) -> str:
    """El hash de una contraseña, con el formato pbkdf2_sha256$iteraciones$sal$hash."""
    sal = sal or secrets.token_bytes(16)
    clave = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, ITERACIONES)
    return "$".join(["pbkdf2_sha256", str(ITERACIONES), base64.b64encode(sal).decode(), base64.b64encode(clave).decode()])


def password_correcta(password: str, guardado: str) -> bool:
    try:
        _, iteraciones, sal, clave = guardado.split("$")
        calculada = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(sal), int(iteraciones))
    except ValueError:
        return False
    # compare_digest tarda lo mismo aunque difieran al principio: no da pistas a un atacante.
    return hmac.compare_digest(calculada, base64.b64decode(clave))


def crear_token(usuario: Usuario, tipo: str) -> str:
    duracion = DURACION_ACCESO if tipo == "access" else DURACION_REFRESCO
    datos = {"sub": str(usuario.id), "tipo": tipo, "exp": datetime.now(timezone.utc) + duracion}
    return jwt.encode(datos, SECRET_KEY, algorithm="HS256")


def usuario_del_token(token: str, tipo: str, bd: Sesion) -> Usuario | None:
    """El usuario dueño del token, o None si el token no es válido, venció o es de otro tipo."""
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None
    if datos.get("tipo") != tipo:
        return None
    usuario = bd.get(Usuario, int(datos["sub"]))
    return usuario if usuario is not None and usuario.activo else None


_bearer = HTTPBearer(auto_error=False)


def usuario_actual(bd: Sesion, credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]) -> Usuario:
    """El usuario del encabezado Authorization: Bearer <token>. Sin token o con uno que no sirve: 401."""
    if credenciales is None:
        raise HTTPException(401, "Las credenciales de autenticación no se proveyeron.", {"WWW-Authenticate": "Bearer"})
    usuario = usuario_del_token(credenciales.credentials, "access", bd)
    if usuario is None:
        raise HTTPException(401, "El token no es válido o expiró.", {"WWW-Authenticate": "Bearer"})
    return usuario


# Uso en una ruta que pide login:  def crear(datos: ..., bd: SesionBD, usuario: UsuarioActual): ...
UsuarioActual = Annotated[Usuario, Depends(usuario_actual)]
