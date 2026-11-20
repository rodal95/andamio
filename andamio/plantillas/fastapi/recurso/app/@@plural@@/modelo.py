# guía: El modelo (la tabla) y la forma de los datos que entran y salen de la API.
# guía: Lo usa router.py. Si un dato no cumple el tipo, la API responde 422 con el motivo.
"""Modelos de @@titulo@@ con SQLModel: cada clase es una tabla o la forma de los datos de la API."""

@@imports_modelo@@
from sqlmodel import Field, SQLModel

@@import_tipos@@


class @@Nombre@@Base(SQLModel):
    """Los campos que se cargan desde la API."""

    @@campos_base@@


class @@Nombre@@(@@Nombre@@Base, table=True):
    """La tabla @@plural@@ de la base de datos."""

    __tablename__ = "@@plural@@"

    id: int | None = Field(default=None, primary_key=True)
    # Fechas que se completan solas: al crear y en cada modificación.
    creado: datetime = Field(default_factory=ahora)
    actualizado: datetime = Field(default_factory=ahora)


class @@Nombre@@Crear(@@Nombre@@Base):
    """Lo que hay que enviar para crear (POST) o reemplazar (PUT)."""

    # TODO(logica): validaciones propias, además del tipo. Ejemplo con un precio
    # (from pydantic import field_validator):
    # @field_validator("precio")
    # @classmethod
    # def precio_positivo(cls, valor):
    #     if valor <= 0:
    #         raise ValueError("El precio tiene que ser mayor que cero.")
    #     return valor


class @@Nombre@@Actualizar(SQLModel):
    """Lo que se puede enviar para modificar (PATCH): solo los campos que cambian."""

    @@campos_opcionales@@


class @@Nombre@@Leer(@@Nombre@@Base):
    """Lo que devuelve la API."""

    id: int
    creado: FechaHora
    actualizado: FechaHora
    @@campos_leer@@
