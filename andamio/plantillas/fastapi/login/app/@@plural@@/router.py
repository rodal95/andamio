# guía: La API del login: registrarse, pedir el token, renovarlo y saber quién es el usuario.
"""Login con JWT: /api/token/, /api/token/refresh/, /api/registro/ y /api/yo/.

Responde igual que la API de Django con nuevo login: el login de React, Vue o React Native
generado con andamio funciona con las dos.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.db import Sesion as SesionBD

from .modelo import Credenciales, Refresco, Registro, Usuario, UsuarioLeer
from .seguridad import (
    UsuarioActual,
    crear_token,
    hash_de,
    puede_ingresar,
    usuario_del_token,
)

router = APIRouter(prefix="/api", tags=["Login"])

CREDENCIALES_INCORRECTAS = "No se encontró una cuenta de usuario activa para las credenciales dadas"


def problemas_de_la_password(password: str, username: str) -> list[str]:
    """Reglas para una contraseña (las mismas ideas que Django)."""
    # TODO(logica): más reglas si las necesitás (ej.: que tenga una mayúscula).
    problemas = []
    if len(password) < 8:
        problemas.append("La contraseña es demasiado corta. Debe contener al menos 8 caracteres.")
    if password.isdigit():
        problemas.append("La contraseña está completamente en numérico.")
    if username and username.lower() in password.lower():
        problemas.append("La contraseña es demasiado similar al nombre de usuario.")
    return problemas


@router.post("/registro/", response_model=UsuarioLeer, status_code=201)
def registrarse(datos: Registro, bd: SesionBD):
    errores = {}
    if bd.exec(select(Usuario).where(Usuario.username == datos.username)).first():
        errores["username"] = ["Ya existe un usuario con este nombre."]
    problemas = problemas_de_la_password(datos.password, datos.username)
    if problemas:
        errores["password"] = problemas
    if errores:
        # El mismo formato que los demás errores: {"campo": ["mensaje"]}.
        return JSONResponse(status_code=400, content=errores)
    usuario = Usuario(**datos.model_dump(exclude={"password"}), password_hash=hash_de(datos.password))
    bd.add(usuario)
    bd.commit()
    bd.refresh(usuario)
    return usuario


@router.post("/token/")
def pedir_token(datos: Credenciales, bd: SesionBD):
    """Con usuario y contraseña, devuelve el token de acceso y el de refresco."""
    usuario = bd.exec(select(Usuario).where(Usuario.username == datos.username)).first()
    if not puede_ingresar(usuario, datos.password):
        raise HTTPException(401, CREDENCIALES_INCORRECTAS)
    return {"access": crear_token(usuario, "access"), "refresh": crear_token(usuario, "refresh")}


@router.post("/token/refresh/")
def renovar_token(datos: Refresco, bd: SesionBD):
    """Con el token de refresco, devuelve un token de acceso nuevo."""
    usuario = usuario_del_token(datos.refresh, "refresh", bd)
    if usuario is None:
        raise HTTPException(401, "El token no es válido o expiró.")
    return {"access": crear_token(usuario, "access")}


@router.get("/yo/", response_model=UsuarioLeer)
def yo(usuario: UsuarioActual):
    """El usuario dueño del token (sin token: 401)."""
    return usuario
