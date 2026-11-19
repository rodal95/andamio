"""Campos de una pieza: "precio:decimal" -> Campo(nombre="precio", tipo="decimal")."""

from __future__ import annotations

from dataclasses import dataclass

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import titulo, validar_nombre_campo

TIPO_POR_DEFECTO = "str"


@dataclass(frozen=True)
class Campo:
    nombre: str  # snake_case
    tipo: str

    @property
    def titulo(self) -> str:
        return titulo(self.nombre.split("_"))


def validar_tipo(tipo: str, tipos: dict[str, str]) -> str:
    tipo = tipo.strip().lower()
    if tipo not in tipos:
        raise AndamioError(
            f"El tipo '{tipo}' no existe en este proyecto.",
            "Tipos válidos: " + ", ".join(tipos),
        )
    return tipo


def parsear_campo(texto: str, tipos: dict[str, str], reservados: dict[str, str] | None = None) -> Campo:
    """Lee "nombre:tipo". Si no se indica tipo, se usa "str"."""
    nombre, separador, tipo = texto.partition(":")
    if separador and not tipo.strip():
        raise AndamioError(f"Al campo '{texto}' le falta el tipo después de ':'.", "Ejemplo: precio:decimal")
    return Campo(
        validar_nombre_campo(nombre, reservados),
        validar_tipo(tipo or TIPO_POR_DEFECTO, tipos),
    )


def validar_campos(campos: list[Campo]) -> None:
    vistos: set[str] = set()
    for campo in campos:
        if campo.nombre in vistos:
            raise AndamioError(f"El campo '{campo.nombre}' está repetido.")
        vistos.add(campo.nombre)
