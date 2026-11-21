"""Relaciones entre piezas: el campo `categoria:fk` apunta a la pieza `categoria`, que ya existe.

El nombre del campo es el de la pieza a la que apunta (en singular). De esa pieza se toma,
del historial, el plural (la tabla o la app) y sus campos (para mostrar su texto en lugar
del id). Cada stack controla que la pieza exista en su forma: la app de Django, la entidad
de Python, el servicio de React.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from andamio.nucleo import historial
from andamio.nucleo.campos import Campo
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre

TIPO = "fk"


def descripcion(que: str) -> str:
    return f"relación con {que} que ya existe (guarda su id): categoria:fk"


@dataclass(frozen=True)
class Relacion:
    campo: Campo
    destino: Nombre  # la pieza a la que apunta, con su plural
    campos: list[Campo] = field(default_factory=list)  # los campos del destino (del historial)

    @property
    def texto(self) -> str | None:
        """El campo de texto del destino que lo identifica (ej.: nombre), o None."""
        return next((c.nombre for c in self.campos if c.tipo in ("str", "email")), None)


def de_campos(raiz: Path, campos: list[Campo], propio: Nombre, piezas: tuple[str, ...]) -> list[Relacion]:
    """Las relaciones de una pieza (sus campos :fk), con lo que se sabe de cada destino."""
    relaciones = []
    for campo in campos:
        if campo.tipo != TIPO:
            continue
        if campo.nombre == propio.snake:
            raise AndamioError(
                f"El campo '{campo.nombre}:fk' apunta a la misma pieza que estás generando.",
                "Las relaciones de una pieza consigo misma todavía no se generan: agregá ese campo a mano.",
            )
        entrada = historial.ultima(raiz, campo.nombre, piezas)
        destino = entrada.nombre if entrada else Nombre.desde_palabras(campo.nombre.split("_"))
        relaciones.append(Relacion(campo, destino, list(entrada.campos) if entrada else []))
    return relaciones


def falta(campo: Campo, que: str, comando: str) -> AndamioError:
    """El error cuando la pieza a la que apunta un :fk todavía no existe."""
    return AndamioError(
        f"El campo '{campo.nombre}:fk' es una relación con {que}, que todavía no existe.",
        f"Generalo primero: {comando}",
    )
