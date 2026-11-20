"""El "mapa de lectura" que se muestra después de generar una pieza.

Para que el código generado no sea una caja negra: en qué orden conviene leer los
archivos (y qué hace cada uno), dónde va la lógica propia (las marcas TODO(logica)) y,
con los pasos de siempre, cómo probarlo.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from andamio.nucleo import consola
from andamio.nucleo.motor import renderizar
from andamio.nucleo.plan import Plan

MARCA_LOGICA = "TODO(logica)"


@dataclass(frozen=True)
class Pendiente:
    """Una marca TODO(logica): dónde escribir lógica propia."""

    archivo: str  # ruta relativa a la raíz del proyecto
    linea: int
    texto: str  # lo que dice la marca, sin el comentario


def texto_de_marca(linea: str) -> str:
    """'    # TODO(logica): validá que el precio sea positivo.' -> 'validá que el precio...'"""
    resto = linea.split(MARCA_LOGICA, 1)[1]
    resto = resto.lstrip(":").strip()
    for cierre in ("*/}", "*/", "-->", "#}"):
        if resto.endswith(cierre):
            resto = resto[: -len(cierre)].rstrip()
    return resto


def buscar_marcas(texto: str, archivo: str) -> list[Pendiente]:
    return [
        Pendiente(archivo, numero, texto_de_marca(linea))
        for numero, linea in enumerate(texto.splitlines(), 1)
        if MARCA_LOGICA in linea
    ]


def marcas_del_plan(plan: Plan) -> list[Pendiente]:
    """Las marcas TODO(logica) de los archivos que el plan crea (todavía en memoria)."""
    pendientes: list[Pendiente] = []
    for ruta, nuevo in sorted(plan.nuevos.items(), key=lambda item: plan.rel(item[0]).lower()):
        try:
            texto = nuevo.contenido.decode("utf-8")
        except UnicodeDecodeError:
            continue
        pendientes += buscar_marcas(texto, Path(plan.rel(ruta)).as_posix())
    return pendientes


def orden_de_lectura(lectura: tuple[tuple[str, str], ...], contexto: dict[str, str]) -> list[tuple[str, str]]:
    return [(renderizar(ruta, contexto), renderizar(rol, contexto)) for ruta, rol in lectura]


def mostrar(lectura: list[tuple[str, str]], pendientes: list[Pendiente]) -> None:
    if lectura:
        consola.escribir()
        consola.titulo("Para entender lo que se generó, leé en este orden:")
        ancho = max(len(ruta) for ruta, _ in lectura)
        for numero, (ruta, rol) in enumerate(lectura, 1):
            consola.escribir(f"  {numero}. {ruta.ljust(ancho)}  " + consola.color(rol, "gris"))
    if pendientes:
        consola.escribir()
        consola.titulo("Dónde va tu lógica (buscá TODO(logica) en el código):")
        ubicaciones = [f"{p.archivo}:{p.linea}" for p in pendientes]
        ancho = max(len(u) for u in ubicaciones)
        for ubicacion, pendiente in zip(ubicaciones, pendientes):
            consola.escribir(f"  {ubicacion.ljust(ancho)}  {pendiente.texto}")
