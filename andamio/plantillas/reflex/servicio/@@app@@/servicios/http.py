"""Pedidos a la API: la de Django, FastAPI o Express hecha con andamio.

La dirección sale de API_URL (archivo .env). Si cambiás el .env, reiniciá reflex run.
Los pedidos los hace la parte de Python de Reflex, así que no hace falta configurar CORS.
"""

import os

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000/api").rstrip("/")


class ErrorApi(Exception):
    """Error que devuelve la API (ej.: 400 con los errores de validación de cada campo)."""

    def __init__(self, estado: int, detalle, mensaje: str = ""):
        super().__init__(mensaje or f"La API respondió con el error {estado}")
        self.estado = estado
        self.detalle = detalle


async def pedir(metodo: str, ruta: str, datos: dict | None = None):
    """Hace un pedido a la API y devuelve el JSON de la respuesta (None si no tiene)."""
    try:
        async with httpx.AsyncClient(timeout=10) as cliente:
            respuesta = await cliente.request(metodo, API_URL + ruta, json=datos)
    except httpx.HTTPError as error:
        raise ErrorApi(0, None, f"No se pudo conectar con la API en {API_URL}. ¿Está andando?") from error
    if respuesta.is_error:
        try:
            detalle = respuesta.json()
        except ValueError:
            detalle = None
        raise ErrorApi(respuesta.status_code, detalle)
    return respuesta.json() if respuesta.content else None
