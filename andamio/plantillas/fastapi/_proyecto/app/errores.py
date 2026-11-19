"""Errores de validación en español y con el formato de Django REST Framework.

FastAPI responde 422 con una lista en inglés. Acá se convierte en 400 con
{"campo": ["mensaje"]}, que es lo que esperan los formularios generados por andamio.
Los errores que no son de un campo (por ejemplo, un JSON mal escrito) van en "general".
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
    "json_invalid": "Los datos enviados no son un JSON válido.",
}


def _mensaje(error: dict) -> str:
    if error["type"] == "value_error" and "email" in error.get("msg", ""):
        return "Introduzca una dirección de correo electrónico válida."
    plantilla = MENSAJES.get(error["type"])
    return plantilla.format(**error.get("ctx", {})) if plantilla else error.get("msg", "Dato inválido.")


async def errores_de_validacion(request: Request, error: RequestValidationError) -> JSONResponse:
    detalles = error.errors()
    # Un id que no es un número (/api/productos/abc/) no existe: 404, igual que en Django.
    if any(detalle["loc"][0] == "path" for detalle in detalles):
        return JSONResponse(status_code=404, content={"detail": "No encontrado."})
    errores: dict[str, list[str]] = {}
    for detalle in detalles:
        # loc es ("body", "precio") o ("query", "stock"); un número es una posición en el texto.
        nombres = [parte for parte in detalle["loc"][1:] if isinstance(parte, str)]
        campo = nombres[0] if nombres else "general"
        errores.setdefault(campo, []).append(_mensaje(detalle))
    return JSONResponse(status_code=400, content=errores)
