"""Registro de stacks.

El orden de REGISTRO es el orden de detección (el primero que coincide gana).
ORDEN_MENU es el orden en que se ofrecen al crear un proyecto.
"""

from __future__ import annotations

from andamio.stacks import python
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

# Orden de detección de la especificación: django, react-native, react, python.
REGISTRO: list[Stack] = [python.STACK]
ORDEN_MENU: list[Stack] = [python.STACK]


def por_clave(clave: str) -> Stack | None:
    clave = clave.strip().lower().replace("_", "-")
    for stack in REGISTRO:
        if stack.clave == clave:
            return stack
    return None


__all__ = ["REGISTRO", "ORDEN_MENU", "por_clave", "Insercion", "Pieza", "Solicitud", "Stack"]
