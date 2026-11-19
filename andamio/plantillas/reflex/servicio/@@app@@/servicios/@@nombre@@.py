"""Funciones para usar el recurso @@titulo@@ de la API: /api/@@plural@@/

Cada @@nombre@@ es un diccionario con id, creado, actualizado y estos campos:
@@campos_doc@@
"""

from @@app@@.servicios.http import pedir

# Con barra al final: así son las rutas de las APIs que genera andamio.
RUTA = "/@@plural@@/"


async def listar() -> list[dict]:
    return await pedir("GET", RUTA)


async def obtener(id_@@nombre@@: int) -> dict:
    return await pedir("GET", f"{RUTA}{id_@@nombre@@}/")


async def crear(datos: dict) -> dict:
    return await pedir("POST", RUTA, datos)


async def actualizar(id_@@nombre@@: int, datos: dict) -> dict:
    """Modifica solo los campos que mandes."""
    return await pedir("PATCH", f"{RUTA}{id_@@nombre@@}/", datos)


async def eliminar(id_@@nombre@@: int) -> None:
    await pedir("DELETE", f"{RUTA}{id_@@nombre@@}/")
