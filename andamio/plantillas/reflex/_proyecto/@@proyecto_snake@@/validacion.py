"""Validación de los formularios, con los mensajes en español de Django REST Framework.

Pydantic (que usa SQLModel) avisa los errores en inglés. errores_de() los convierte
en {"campo": ["mensaje"]}, que es lo que muestran los formularios.
"""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, ValidationError


def _con_zona_horaria(valor: datetime) -> datetime:
    """Sin zona horaria (como la manda un <input type="datetime-local">) es la hora de esta PC."""
    return valor if valor.tzinfo else valor.astimezone()


# Fecha y hora: "2026-11-19T10:30" se toma como hora de esta PC y se guarda con su zona.
FechaHora = Annotated[datetime, AfterValidator(_con_zona_horaria)]

MENSAJES = {
    "missing": "Este campo es requerido.",
    "string_too_short": "Este campo no puede estar en blanco.",
    "string_too_long": "Asegúrese de que este campo no tenga más de {max_length} caracteres.",
    "string_type": "Introduzca un texto válido.",
    "int_parsing": "Introduzca un número entero válido.",
    "int_from_float": "Introduzca un número entero válido.",
    "int_type": "Introduzca un número entero válido.",
    "float_parsing": "Introduzca un número válido.",
    "float_type": "Introduzca un número válido.",
    "decimal_parsing": "Introduzca un número válido.",
    "decimal_type": "Introduzca un número válido.",
    "decimal_max_digits": "Asegúrese de que no haya más de {max_digits} dígitos en total.",
    "decimal_max_places": "Asegúrese de que no haya más de {decimal_places} decimales.",
    "decimal_whole_digits": "Asegúrese de que no haya más de {whole_digits} dígitos antes del punto decimal.",
    "bool_parsing": "Tiene que ser verdadero o falso.",
    "bool_type": "Tiene que ser verdadero o falso.",
    "date_parsing": "Fecha con formato erróneo. Use AAAA-MM-DD.",
    "date_from_datetime_parsing": "Fecha con formato erróneo. Use AAAA-MM-DD.",
    "date_type": "Fecha con formato erróneo. Use AAAA-MM-DD.",
    "datetime_parsing": "Fecha y hora con formato erróneo.",
    "datetime_from_date_parsing": "Fecha y hora con formato erróneo.",
    "datetime_type": "Fecha y hora con formato erróneo.",
}


def _mensaje(error: dict) -> str:
    if error["type"] == "value_error" and "email" in error.get("msg", ""):
        return "Introduzca una dirección de correo electrónico válida."
    plantilla = MENSAJES.get(error["type"])
    return plantilla.format(**error.get("ctx", {})) if plantilla else error.get("msg", "Dato inválido.")


def errores_de(error: ValidationError) -> dict[str, list[str]]:
    """{"precio": ["Introduzca un número válido."], ...} a partir de un error de Pydantic."""
    errores: dict[str, list[str]] = {}
    for detalle in error.errors():
        nombres = [parte for parte in detalle["loc"] if isinstance(parte, str)]
        errores.setdefault(nombres[0] if nombres else "general", []).append(_mensaje(detalle))
    return errores
