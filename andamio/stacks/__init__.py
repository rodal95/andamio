"""Registro de stacks.

El orden de REGISTRO es el orden de detección (el primero que coincide gana).
ORDEN_MENU es el orden en que se ofrecen al crear un proyecto.
"""

from __future__ import annotations

from andamio.stacks import django, express, fastapi, next, python, react, react_native
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

# Orden de detección: django, fastapi, react-native, next-fullstack, next, react, express, python.
# - next-fullstack antes que next: los dos tienen next; el full stack, además, Prisma.
# - Express va después de React y Next: un proyecto de React con express (para un
#   servidor propio) sigue siendo un proyecto de React.
REGISTRO: list[Stack] = [
    django.STACK,
    fastapi.STACK,
    react_native.STACK,
    next.STACK_FULLSTACK,
    next.STACK,
    react.STACK,
    express.STACK,
    python.STACK,
]
# En el menú: primero los backends, después los frontends y al final el full stack.
ORDEN_MENU: list[Stack] = [
    python.STACK,
    django.STACK,
    fastapi.STACK,
    express.STACK,
    react.STACK,
    react_native.STACK,
    next.STACK,
    next.STACK_FULLSTACK,
]


def por_clave(clave: str) -> Stack | None:
    clave = clave.strip().lower().replace("_", "-")
    for stack in REGISTRO:
        if stack.clave == clave:
            return stack
    return None


__all__ = ["REGISTRO", "ORDEN_MENU", "por_clave", "Insercion", "Pieza", "Solicitud", "Stack"]
