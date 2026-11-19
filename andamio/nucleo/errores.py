"""Errores que andamio muestra al alumno sin traceback."""

from __future__ import annotations


class AndamioError(Exception):
    """Error esperable: se muestra el mensaje (y una sugerencia) en lugar de un traceback."""

    def __init__(self, mensaje: str, sugerencia: str | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.sugerencia = sugerencia


class Cancelado(Exception):
    """El alumno canceló la operación (respondió que no, Ctrl+C o cerró la entrada)."""
