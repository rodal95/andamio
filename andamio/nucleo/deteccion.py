"""Detección del tipo de proyecto, subiendo por las carpetas como hace git."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError

if TYPE_CHECKING:
    from andamio.stacks.base import Stack


def leer_package_json(carpeta: Path) -> dict | None:
    archivo = carpeta / "package.json"
    if not archivo.is_file():
        return None
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return datos if isinstance(datos, dict) else None


def dependencias_npm(carpeta: Path) -> set[str]:
    datos = leer_package_json(carpeta) or {}
    nombres: set[str] = set()
    for clave in ("dependencies", "devDependencies"):
        seccion = datos.get(clave)
        if isinstance(seccion, dict):
            nombres.update(seccion)
    return nombres


def buscar_proyecto(desde: Path, registro: Sequence[Stack] | None = None) -> tuple[Stack, Path] | None:
    """Devuelve (stack, raíz) del proyecto más cercano, o None.

    En cada carpeta se prueban los stacks en el orden del registro; gana la carpeta
    más cercana (un frontend/ dentro de un backend/ se detecta como frontend).
    """
    if registro is None:
        from andamio.stacks import REGISTRO as registro
    desde = desde.resolve()
    for carpeta in (desde, *desde.parents):
        configurado = _stack_de_andamio_json(carpeta, registro)
        if configurado is not None:
            return configurado, carpeta
        for stack in registro:
            try:
                if stack.detectar(carpeta):
                    return stack, carpeta
            except OSError:
                continue
    return None


def _stack_de_andamio_json(carpeta: Path, registro: Sequence[Stack]) -> Stack | None:
    """El stack que indica andamio.json en esa carpeta (si lo indica)."""
    from andamio.nucleo import ajustes

    configuracion = ajustes.leer(carpeta)
    if configuracion is None or configuracion.stack is None:
        return None
    for stack in registro:
        if stack.clave == configuracion.stack:
            return stack
    claves = ", ".join(s.clave for s in registro)
    raise AndamioError(
        f"{ajustes.ARCHIVO} ({carpeta}): el stack '{configuracion.stack}' no existe.", f"Stacks: {claves}"
    )


def error_no_detectado(desde: Path, registro: Sequence[Stack] | None = None) -> AndamioError:
    if registro is None:
        from andamio.stacks import REGISTRO as registro
    senales = "\n".join(f"  - {s.titulo}: {s.senal}" for s in registro)
    return AndamioError(
        f"No encontré un proyecto en {desde} ni en las carpetas de arriba.\nBusqué:\n{senales}",
        f"Entrá a la carpeta de tu proyecto con cd, o creá uno nuevo con: {consola.programa()} crear <tipo> <nombre>",
    )
