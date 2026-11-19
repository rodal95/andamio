"""Arma el Plan de cambios a partir de un stack, una pieza y los datos del alumno."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from andamio.nucleo import plantillas
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.motor import renderizar, renderizar_ruta
from andamio.nucleo.nombres import (
    Nombre,
    kebab,
    pascal,
    pluralizar,
    separar_palabras,
    snake,
    titulo,
    validar_nombre,
)
from andamio.nucleo.plan import Plan

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

    from andamio.stacks.base import Pieza, Solicitud, Stack


# --- Nombres ----------------------------------------------------------------


def nombre_para_pieza(pieza: Pieza, texto: str, plural: str | None = None) -> Nombre:
    palabras = separar_palabras(texto)
    if pieza.ajustar_palabras:
        palabras = pieza.ajustar_palabras(palabras)
        if not palabras:
            raise AndamioError(f"Al nombre '{texto}' le falta la parte principal.")
    plural_palabras = separar_palabras(plural, "El plural") if plural else pluralizar(palabras)
    return Nombre.desde_palabras(palabras, plural_palabras)


def validar_nombre_pieza(stack: Stack, raiz: Path, nombre: Nombre) -> None:
    reservados = stack.reservados(raiz) if stack.reservados else {}
    validar_nombre(nombre, reservados)


def describir_nombre(pieza: Pieza, nombre: Nombre) -> str:
    formas: list[str] = []
    for forma in pieza.formas:
        valor = nombre.forma(forma)
        if valor not in formas:
            formas.append(valor)
    texto = " / ".join(formas)
    if pieza.usa_plural:
        texto += f"  (plural: {nombre.plural})"
    return texto


def carpeta_proyecto(texto: str) -> str:
    return kebab(separar_palabras(texto, "El nombre del proyecto"))


# --- Plantillas -------------------------------------------------------------


def _base(stack: Stack) -> Traversable:
    return stack.plantillas if stack.plantillas is not None else plantillas.carpeta_incorporada(stack.clave)


def ubicar_plantilla(stack: Stack, pieza: Pieza, raiz: Path) -> tuple[Traversable, bool]:
    """Devuelve la carpeta de plantillas a usar y si es la personalizada por el alumno."""
    propia = plantillas.carpeta_personalizada(raiz, stack.clave, pieza.clave)
    if propia.is_dir():
        return propia, True
    return _base(stack) / pieza.clave, False


# --- Piezas -----------------------------------------------------------------


def contexto_pieza(sol: Solicitud) -> dict[str, str]:
    contexto = sol.nombre.marcadores()
    if sol.pieza.contexto:
        contexto.update(sol.pieza.contexto(sol))
    return contexto


def planificar_pieza(sol: Solicitud) -> Plan:
    stack, pieza = sol.stack, sol.pieza
    sol.contexto = contexto = contexto_pieza(sol)
    plan = Plan(sol.raiz)

    for ruta in pieza.existe_si:
        plan.exigir_inexistente(renderizar_ruta(tuple(ruta.split("/")), contexto, ruta))

    carpeta, _ = ubicar_plantilla(stack, pieza, sol.raiz)
    if not carpeta.is_dir():
        raise AndamioError(f"No encontré las plantillas de '{pieza.clave}' en {carpeta}.")
    for archivo in plantillas.leer_arbol(carpeta):
        origen = f"{stack.clave}/{pieza.clave}/{archivo.ruta}"
        destino = renderizar_ruta(archivo.partes, contexto, origen)
        texto = archivo.texto
        contenido = renderizar(texto, contexto, origen) if texto is not None else archivo.contenido
        plan.crear(destino, contenido, si_no_existe=archivo.ruta in pieza.si_no_existe)

    for ins in pieza.inserciones:
        origen = f"inserción en {ins.archivo}"
        plan.insertar(
            renderizar_ruta(tuple(ins.archivo.split("/")), contexto, origen),
            renderizar(ins.texto, contexto, origen),
            marcador=ins.marcador,
            descripcion=renderizar(ins.descripcion, contexto, origen),
            comentario=ins.comentario,
            crear_si_falta=ins.crear_si_falta,
            ubicacion=renderizar(ins.ubicacion, contexto, origen),
        )
    return plan


def pasos_pieza(sol: Solicitud) -> list[str]:
    pasos = sol.pieza.siguiente_paso
    lista = pasos(sol) if callable(pasos) else pasos
    return [renderizar(p, sol.contexto) for p in lista]


# --- Proyectos --------------------------------------------------------------


def contexto_proyecto(stack: Stack, texto: str) -> dict[str, str]:
    palabras = separar_palabras(texto, "El nombre del proyecto")
    contexto = {
        "carpeta": kebab(palabras),
        "proyecto": kebab(palabras),
        "proyecto_snake": snake(palabras),
        "Proyecto": pascal(palabras),
        "proyectoTitulo": titulo(palabras),
    }
    if stack.contexto_proyecto:
        contexto.update(stack.contexto_proyecto(Nombre.desde_palabras(palabras)))
    return contexto


def planificar_proyecto(stack: Stack, texto: str, padre: Path) -> tuple[Plan, dict[str, str]]:
    contexto = contexto_proyecto(stack, texto)
    nombre_carpeta = contexto["carpeta"]
    destino = padre / nombre_carpeta
    if destino.exists() and (not destino.is_dir() or any(destino.iterdir())):
        raise AndamioError(
            f"Ya existe '{nombre_carpeta}' en {padre} y no está vacía.",
            "Elegí otro nombre para el proyecto, o creálo en otra carpeta.",
        )
    plan = Plan(padre)
    plan.crear_carpeta(nombre_carpeta)
    base = PurePosixPath(nombre_carpeta)
    for archivo in plantillas.leer_arbol(_base(stack) / plantillas.CARPETA_PROYECTO, ignorar_leeme=False):
        origen = f"{stack.clave}/{plantillas.CARPETA_PROYECTO}/{archivo.ruta}"
        destino_rel = base / renderizar_ruta(archivo.partes, contexto, origen)
        texto_plantilla = archivo.texto
        if texto_plantilla is None:
            plan.crear(destino_rel, archivo.contenido)
            continue
        plan.crear(destino_rel, renderizar(texto_plantilla, contexto, origen))
        if archivo.ruta == ".env.example" and stack.contexto_env:
            plan.crear(base / ".env", renderizar(texto_plantilla, {**contexto, **stack.contexto_env()}, origen))
    return plan, contexto


def pasos_proyecto(stack: Stack, contexto: dict[str, str]) -> list[str]:
    return [renderizar(p, contexto) for p in stack.siguiente_paso_proyecto]
