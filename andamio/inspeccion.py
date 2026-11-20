"""Comandos que miran el proyecto sin generar nada: `pendientes`.

`pendientes` busca las marcas TODO(logica) que deja andamio en el código generado: son
los lugares donde va la lógica propia (validaciones, reglas de negocio, cálculos).
"""

from __future__ import annotations

import os
from pathlib import Path

from andamio.nucleo import consola
from andamio.nucleo.deteccion import buscar_proyecto
from andamio.nucleo.lectura import MARCA_LOGICA, Pendiente, buscar_marcas

# Carpetas que no son código del proyecto (dependencias, compilados, copias de plantillas).
CARPETAS_IGNORADAS = frozenset(
    {
        "node_modules", ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
        ".next", ".web", ".expo", "dist", "build", "out", "coverage", ".andamio", "staticfiles",
    }
)
# Archivos donde puede haber código (los .md no: pueden explicar qué es una marca).
EXTENSIONES = frozenset(
    {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".html", ".css", ".prisma", ".sql", ".http"}
)


def raiz_del_proyecto(cwd: Path) -> Path:
    encontrado = buscar_proyecto(cwd)
    return encontrado[1] if encontrado else cwd


def buscar_pendientes(raiz: Path) -> list[Pendiente]:
    pendientes: list[Pendiente] = []
    for carpeta, subcarpetas, archivos in os.walk(raiz):
        subcarpetas[:] = sorted(s for s in subcarpetas if s not in CARPETAS_IGNORADAS)
        for nombre in sorted(archivos):
            ruta = Path(carpeta, nombre)
            if ruta.suffix not in EXTENSIONES:
                continue
            try:
                texto = ruta.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if MARCA_LOGICA in texto:
                pendientes += buscar_marcas(texto, ruta.relative_to(raiz).as_posix())
    return pendientes


def pendientes(cwd: Path) -> int:
    raiz = raiz_del_proyecto(cwd)
    encontrados = buscar_pendientes(raiz)
    if not encontrados:
        consola.exito(f"No hay marcas {MARCA_LOGICA} en {raiz}.")
        consola.escribir("Cuando generes una pieza, andamio marca así los lugares donde va tu lógica.")
        return 0
    consola.titulo(f"Lógica por escribir ({MARCA_LOGICA}) en {raiz}:")
    archivo_actual = None
    for pendiente in encontrados:
        if pendiente.archivo != archivo_actual:
            archivo_actual = pendiente.archivo
            consola.escribir()
            consola.escribir(consola.color(archivo_actual, "negrita"))
        consola.escribir(f"  {str(pendiente.linea).rjust(4)}  {pendiente.texto}")
    archivos = len({p.archivo for p in encontrados})
    consola.escribir()
    consola.escribir(
        f"{len(encontrados)} {'marca' if len(encontrados) == 1 else 'marcas'} en "
        f"{archivos} {'archivo' if archivos == 1 else 'archivos'}. "
        "Cuando escribas esa lógica, borrá la marca y deja de aparecer acá."
    )
    return 0
