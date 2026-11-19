"""Conexión a la base de datos (SQLite por defecto)."""

import warnings
from typing import Annotated

from fastapi import Depends
from sqlalchemy import exc as sa_exc
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

# SQLite guarda los decimales como texto y SQLAlchemy lo avisa; acá no es un problema.
warnings.filterwarnings("ignore", message=".*Decimal objects natively.*", category=sa_exc.SAWarning)

# check_same_thread=False: FastAPI puede atender cada pedido en un hilo distinto.
argumentos = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=argumentos)


def crear_tablas():
    """Crea las tablas que todavía no existen (no modifica las que ya están)."""
    SQLModel.metadata.create_all(engine)


def get_sesion():
    """Una sesión de base de datos por pedido; se cierra sola al terminar."""
    with Session(engine) as sesion:
        yield sesion


# Uso en una ruta:  def listar(sesion: Sesion): ...
Sesion = Annotated[Session, Depends(get_sesion)]
