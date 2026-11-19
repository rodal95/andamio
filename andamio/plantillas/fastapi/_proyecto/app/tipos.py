"""Tipos y funciones que usan todos los recursos."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, PlainSerializer

from app.config import ZONA_HORARIA

# Un decimal que en el JSON sale como número (10.5) y no como texto ("10.50"),
# igual que en la API de Django. Así los servicios de React lo reciben como number.
DecimalNumero = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


def _con_zona_horaria(valor: datetime) -> datetime:
    """Sin zona horaria (como la manda un <input type="datetime-local">) es hora local."""
    return valor if valor.tzinfo else valor.replace(tzinfo=ZONA_HORARIA)


def _en_hora_local(valor: datetime) -> str:
    return valor.astimezone(ZONA_HORARIA).isoformat()


# Fecha y hora, igual que en Django: "2026-11-19T10:30" se toma como hora local
# (ZONA_HORARIA) y en el JSON sale con su zona: "2026-11-19T10:30:00-03:00".
FechaHora = Annotated[
    datetime,
    AfterValidator(_con_zona_horaria),
    PlainSerializer(_en_hora_local, return_type=str, when_used="json"),
]


def ahora() -> datetime:
    """La fecha y hora actual, para los campos creado y actualizado."""
    return datetime.now(timezone.utc)
