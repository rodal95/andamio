"""Menú interactivo: lo que se ejecuta al escribir solo `andamio`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from andamio import __version__, acciones, stacks
from andamio.nucleo import consola
from andamio.nucleo.campos import Campo, validar_tipo
from andamio.nucleo.deteccion import buscar_proyecto
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.generador import (
    carpeta_proyecto,
    describir_nombre,
    nombre_variante,
    validar_nombre_pieza,
    variante_del_proyecto,
)
from andamio.nucleo.nombres import Nombre, parece_plural, validar_nombre_campo
from andamio.stacks.base import Pieza, Solicitud, Stack


def ejecutar(cwd: Path) -> int:
    consola.titulo(f"andamio {__version__}")
    encontrado = buscar_proyecto(cwd)
    if encontrado:
        return _menu_piezas(*encontrado)
    return _menu_crear(cwd)


# --- Crear proyecto -----------------------------------------------------------


def _menu_crear(cwd: Path) -> int:
    consola.escribir("No hay un proyecto en esta carpeta.")
    consola.escribir()
    opciones: list[tuple[Stack | None, str]] = [(s, s.titulo) for s in stacks.ORDEN_MENU]
    stack = consola.elegir("¿Qué proyecto querés crear?", opciones + [(None, "Salir")])
    if stack is None:
        return 0
    consola.escribir()

    def validar(texto: str) -> str:
        carpeta = carpeta_proyecto(texto)
        if (cwd / carpeta).exists() and any((cwd / carpeta).iterdir()):
            raise AndamioError(f"Ya existe la carpeta '{carpeta}' y no está vacía. Elegí otro nombre.")
        return texto

    variante = None
    if stack.variantes:
        consola.escribir()
        opciones_variante = [
            (clave, nombre + (" (recomendado)" if i == 0 else "")) for i, (clave, nombre) in enumerate(stack.variantes.items())
        ]
        variante = consola.elegir("¿En qué lenguaje?", opciones_variante)
        consola.escribir()
    texto = consola.preguntar("Nombre del proyecto", validar=validar, ejemplo=stack.ejemplo_proyecto)
    return acciones.crear_proyecto(stack, texto, cwd, confirmar=True, variante=variante)


# --- Generar pieza ------------------------------------------------------------


def _menu_piezas(stack: Stack, raiz: Path) -> int:
    variante = variante_del_proyecto(stack, raiz)
    nombre = nombre_variante(stack, variante)
    consola.exito(f"Proyecto {stack.titulo}" + (f" ({nombre})" if nombre else "") + " detectado.")
    consola.escribir(consola.color(f"Carpeta: {raiz}", "gris"))
    consola.escribir()
    opciones: list[tuple[Pieza | None, str]] = [(p, f"{p.titulo}: {p.descripcion}") for p in stack.piezas.values()]
    pieza = consola.elegir("¿Qué querés generar?", opciones + [(None, "Salir")])
    if pieza is None:
        return 0
    consola.escribir()
    nombre = _pedir_nombre(stack, pieza, raiz)
    extras = _pedir_opciones(pieza)
    campos = _pedir_campos(stack, acciones.campos_reservados(pieza, nombre)) if pieza.usa_campos else []
    consola.escribir()
    sol = Solicitud(stack, pieza, raiz, nombre, campos, extras, variante=variante)
    return acciones.generar_pieza(sol, confirmar=True)


def _pedir_nombre(stack: Stack, pieza: Pieza, raiz: Path) -> Nombre:
    if pieza.nombre_defecto:
        nombre = acciones.preparar_nombre(stack, pieza, raiz, pieza.nombre_defecto, None)
        consola.escribir(f"Se usará: {consola.color(describir_nombre(pieza, nombre), 'negrita')}")
        return nombre
    ejemplo = pieza.ejemplo.split()[0]
    while True:
        nombre = consola.preguntar(
            "Nombre en singular" if pieza.usa_plural else "Nombre",
            validar=lambda t: acciones.preparar_nombre(stack, pieza, raiz, t, None),
            ejemplo=ejemplo,
        )
        if pieza.usa_plural and parece_plural(nombre.palabras):
            consola.aviso(f"'{nombre.snake}' parece estar en plural. Los nombres van en singular (ej: '{ejemplo}').")
            if not consola.confirmar("¿Usarlo igual?", defecto=False):
                continue
        break
    consola.escribir(f"Se usará: {consola.color(describir_nombre(pieza, nombre), 'negrita')}")
    if pieza.usa_plural and not consola.confirmar(f"El plural será '{nombre.plural}'. ¿Está bien?", defecto=True):

        def validar_plural(texto: str) -> Nombre:
            con_plural = nombre.con_plural(texto)
            validar_nombre_pieza(stack, raiz, con_plural, pieza)
            return con_plural

        nombre = consola.preguntar("Escribí el plural", validar=validar_plural)
        consola.escribir(f"Se usará: {consola.color(describir_nombre(pieza, nombre), 'negrita')}")
    return nombre


def _pedir_opciones(pieza: Pieza) -> dict[str, Any]:
    extras: dict[str, Any] = {}
    if "protegido" in pieza.opciones:
        extras["protegido"] = consola.confirmar(
            "¿Proteger el recurso? (solo usuarios con login pueden crear, modificar y eliminar)", defecto=False
        )
    if "carpeta" in pieza.opciones:
        normalizar = pieza.normalizar_opcion.get("carpeta")
        carpeta = consola.preguntar(
            "Carpeta dentro de app/ (Enter para ninguna)",
            validar=normalizar,
            permitir_vacio=True,
            ejemplo="productos o (tabs)",
        )
        if carpeta:
            extras["carpeta"] = carpeta
    return extras


def _pedir_campos(stack: Stack, reservados: dict[str, str]) -> list[Campo]:
    consola.escribir()
    consola.titulo("Campos")
    consola.escribir(consola.color("Escribí un campo por vez. Cuando termines, apretá Enter sin escribir nada.", "gris"))
    campos: list[Campo] = []
    tipos = [(t, f"{t.ljust(9)} {d}") for t, d in stack.tipos.items()]

    def validar(texto: str) -> tuple[str, str | None]:
        nombre, _, tipo = texto.partition(":")
        nombre = validar_nombre_campo(nombre, reservados)
        if nombre in {c.nombre for c in campos}:
            raise AndamioError(f"El campo '{nombre}' ya está en la lista.")
        return nombre, validar_tipo(tipo, stack.tipos) if tipo else None

    while True:
        respuesta = consola.preguntar("Nombre del campo (Enter para terminar)", validar=validar, permitir_vacio=True)
        if not respuesta:
            if campos:
                return campos
            consola.escribir(consola.color("  Agregá al menos un campo.", "amarillo"))
            continue
        nombre, tipo = respuesta
        if tipo is None:
            tipo = consola.elegir(f"Tipo de '{nombre}':", tipos)
        campos.append(Campo(nombre, tipo))
        consola.escribir(consola.color(f"  + {nombre} ({tipo})", "verde"))
