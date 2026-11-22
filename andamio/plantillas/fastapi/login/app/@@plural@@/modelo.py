# guía: El usuario (la tabla) y la forma de los datos del login. Lo usan router.py y seguridad.py.
"""Usuarios del login."""

from typing import Literal

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    """Un usuario. La contraseña nunca se guarda tal cual: se guarda su hash (seguridad.py)."""

    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=150)
    email: str = Field(default="", max_length=254)
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)
    password_hash: str
    activo: bool = True


class UsuarioLeer(SQLModel):
    """Lo que la API devuelve de un usuario (nunca la contraseña). Igual que la API de Django."""

    id: int
    username: str
    email: str
    first_name: str
    last_name: str


class Registro(SQLModel):
    """Lo que hay que enviar para crear un usuario (POST /api/registro/)."""

    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1)
    # El email es opcional: vacío ("") o una dirección válida.
    email: EmailStr | Literal[""] = ""
    first_name: str = Field(default="", max_length=150)
    last_name: str = Field(default="", max_length=150)


class Credenciales(SQLModel):
    """Lo que hay que enviar para pedir el token (POST /api/token/)."""

    username: str
    password: str


class Refresco(SQLModel):
    """Lo que hay que enviar para renovar el token de acceso (POST /api/token/refresh/)."""

    refresh: str
