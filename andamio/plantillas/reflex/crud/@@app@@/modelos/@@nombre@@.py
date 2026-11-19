"""Modelo de @@titulo@@ con SQLModel: la tabla @@plural@@ y los datos que se cargan.

Si cambiás los campos, creá una migración: reflex db makemigrations y reflex db migrate.
"""

@@imports_modelo@@
from sqlmodel import Field, SQLModel

@@import_validacion@@


def ahora() -> datetime:
    """La fecha y hora actual, para los campos creado y actualizado."""
    return datetime.now(UTC)


class @@Nombre@@Datos(SQLModel):
    """Los campos que se cargan desde el formulario, con su validación."""

    @@campos_base@@


class @@Nombre@@(@@Nombre@@Datos, table=True):
    """La tabla @@plural@@ de la base de datos."""

    __tablename__ = "@@plural@@"

    id: int | None = Field(default=None, primary_key=True)
    # Fechas que se completan solas: al crear y en cada modificación.
    creado: datetime = Field(default_factory=ahora)
    actualizado: datetime = Field(default_factory=ahora)
