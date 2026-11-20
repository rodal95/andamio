"""El historial de lo que se generó: .andamio/historial.jsonl.

Cada `nuevo` agrega una línea (JSON) con la pieza, el nombre, el plural, los campos y las
opciones. Se escribe en el mismo plan que los archivos de la pieza: si algo falla, se
deshace con todo lo demás. Con eso, `andamio mapa` puede volver a calcular qué archivos
y qué conexiones tendría que tener cada pieza, y controlar que sigan ahí.

Es un archivo de texto: se puede subir a git (sirve para todo el equipo) o borrar
(`mapa` deja de mostrar lo anterior; nada más cambia).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath

from andamio import __version__
from andamio.nucleo.campos import Campo
from andamio.nucleo.nombres import Nombre

ARCHIVO = PurePosixPath(".andamio") / "historial.jsonl"


@dataclass(frozen=True)
class Entrada:
    pieza: str
    nombre: Nombre
    campos: list[Campo] = field(default_factory=list)
    opciones: dict[str, object] = field(default_factory=dict)
    variante: str = ""
    fecha: str = ""
    version: str = ""

    def resumen(self) -> str:
        campos = " ".join(f"{c.nombre}:{c.tipo}" for c in self.campos)
        opciones = " ".join(f"--{k}" if v is True else f"--{k} {v}" for k, v in self.opciones.items() if v not in (None, False))
        return " ".join(p for p in (self.pieza, self.nombre.snake, campos, opciones) if p)


def linea(pieza: str, nombre: Nombre, campos: list[Campo], opciones: dict, variante: str) -> str:
    datos = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "andamio": __version__,
        "pieza": pieza,
        "nombre": nombre.snake,
        "plural": nombre.plural,
        "campos": [{"nombre": c.nombre, "tipo": c.tipo} for c in campos],
        "opciones": {k: v for k, v in opciones.items() if isinstance(v, (str, bool, int)) and v not in (None, False, "")},
    }
    if variante:
        datos["variante"] = variante
    return json.dumps(datos, ensure_ascii=False)


def leer(raiz: Path) -> tuple[list[Entrada], int]:
    """Las entradas del historial y cuántas líneas no se pudieron leer."""
    try:
        texto = (raiz / ARCHIVO).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return [], 0
    except (OSError, UnicodeDecodeError):
        return [], 1
    entradas: list[Entrada] = []
    malas = 0
    for linea_texto in texto.splitlines():
        if not linea_texto.strip():
            continue
        try:
            datos = json.loads(linea_texto)
            nombre = Nombre(tuple(datos["nombre"].split("_")), tuple(datos["plural"].split("_")))
            entradas.append(
                Entrada(
                    pieza=datos["pieza"],
                    nombre=nombre,
                    campos=[Campo(c["nombre"], c["tipo"]) for c in datos.get("campos", [])],
                    opciones=dict(datos.get("opciones", {})),
                    variante=datos.get("variante", ""),
                    fecha=datos.get("fecha", ""),
                    version=datos.get("andamio", ""),
                )
            )
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
            malas += 1
    return entradas, malas
