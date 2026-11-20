"""Acciones que comparten la línea de comandos y el menú interactivo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from andamio import stacks
from andamio.nucleo import consola, lectura
from andamio.nucleo.campos import Campo, parsear_campo, validar_campos
from andamio.nucleo.deteccion import buscar_proyecto, error_no_detectado
from andamio.nucleo.errores import AndamioError, Cancelado
from andamio.nucleo.generador import (
    describir_nombre,
    nombre_para_pieza,
    pasos_pieza,
    pasos_proyecto,
    nombre_variante,
    planificar_pieza,
    planificar_proyecto,
    resolver_variante,
    ubicar_plantilla,
    validar_nombre_pieza,
    variante_del_proyecto,
)
from andamio.nucleo.nombres import Nombre, parece_plural, quitar_tildes
from andamio.nucleo.plan import Plan
from andamio.stacks.base import Pieza, Solicitud, Stack


def mostrar_pasos(pasos: list[str]) -> None:
    if not pasos:
        return
    consola.escribir()
    consola.titulo("Siguiente paso:" if len(pasos) == 1 else "Siguientes pasos:")
    for paso in pasos:
        if paso.startswith("# "):
            consola.escribir("    " + consola.color(paso[2:], "gris"))
        elif paso.startswith(("http://", "https://")):
            consola.escribir("    Abrí en el navegador: " + consola.comando(paso))
        else:
            consola.escribir("    " + consola.comando(paso))


def _cerrar(plan: Plan, simular: bool, confirmar: bool, pregunta: str) -> bool:
    """Muestra el plan y lo aplica. Devuelve False si fue una simulación."""
    plan.validar()
    if simular:
        plan.mostrar()
        consola.escribir()
        consola.escribir(consola.color("Simulación: no se creó ni modificó ningún archivo.", "amarillo", "negrita"))
        return False
    if confirmar:
        consola.escribir()
        plan.mostrar()
        consola.escribir()
        if not consola.confirmar(pregunta, defecto=True):
            raise Cancelado("No se creó ni modificó ningún archivo.")
    plan.aplicar()
    consola.escribir()
    consola.exito("Listo.")
    plan.mostrar("Archivos creados", "Archivos modificados")
    plan.mostrar_manuales()
    return True


# --- crear --------------------------------------------------------------------


def stack_por_clave(clave: str) -> Stack:
    stack = stacks.por_clave(clave)
    if stack is None:
        disponibles = ", ".join(s.clave for s in stacks.ORDEN_MENU)
        raise AndamioError(f"No conozco el tipo de proyecto '{clave}'.", f"Tipos disponibles: {disponibles}")
    return stack


def crear_proyecto(
    stack: Stack,
    texto_nombre: str,
    padre: Path,
    simular: bool = False,
    confirmar: bool = False,
    variante: str | None = None,
) -> int:
    variante = resolver_variante(stack, variante)
    plan, contexto = planificar_proyecto(stack, texto_nombre, padre, variante)
    consola.escribir(f"Se usará la carpeta: {consola.color(contexto['carpeta'], 'negrita')}")
    if variante:
        consola.escribir(f"Variante: {consola.color(nombre_variante(stack, variante), 'negrita')}")
    existente = buscar_proyecto(padre)
    if existente:
        consola.aviso(
            f"Estás dentro de un proyecto {existente[0].titulo} ({existente[1]}). "
            "El proyecto nuevo se va a crear adentro."
        )
    if _cerrar(plan, simular, confirmar, "¿Crear el proyecto?"):
        mostrar_pasos(pasos_proyecto(stack, contexto))
    return 0


# --- nuevo --------------------------------------------------------------------


def proyecto_actual(cwd: Path) -> tuple[Stack, Path]:
    encontrado = buscar_proyecto(cwd)
    if encontrado is None:
        raise error_no_detectado(cwd)
    return encontrado


# Nombres de las piezas en inglés: "new resource" es lo mismo que "nuevo recurso".
ALIAS_PIEZAS = {
    "entity": "entidad",
    "resource": "recurso",
    "component": "componente",
    "page": "pagina",
    "screen": "pantalla",
    "service": "servicio",
    "state": "estado",
    "theme": "tema",
    "style": "estilo",
}


def clave_de_pieza(texto: str) -> str:
    """"Página", "pagina" y "page" son la misma pieza."""
    clave = quitar_tildes(texto.strip().lower())
    return ALIAS_PIEZAS.get(clave, clave)


def pieza_por_clave(stack: Stack, clave: str) -> Pieza:
    pieza = stack.piezas.get(clave_de_pieza(clave))
    if pieza is None:
        disponibles = ", ".join(stack.piezas)
        raise AndamioError(
            f"'{clave}' no es una pieza que se pueda generar en un proyecto {stack.titulo}.",
            f"Piezas disponibles: {disponibles}",
        )
    return pieza


def validar_opciones(pieza: Pieza, opciones: dict[str, Any]) -> None:
    for clave, valor in opciones.items():
        if valor not in (None, False) and clave not in pieza.opciones:
            raise AndamioError(f"La pieza '{pieza.clave}' no acepta la opción --{clave}.")


def preparar_nombre(stack: Stack, pieza: Pieza, raiz: Path, texto: str, plural: str | None) -> Nombre:
    nombre = nombre_para_pieza(pieza, texto, plural)
    validar_nombre_pieza(stack, raiz, nombre, pieza)
    return nombre


def preparar_opciones(pieza: Pieza, opciones: dict[str, Any]) -> dict[str, Any]:
    """Valida las opciones y normaliza las de texto (ej.: --carpeta "(Tabs)" -> "(tabs)")."""
    validar_opciones(pieza, opciones)
    resultado = {k: v for k, v in opciones.items() if v not in (None, False, "")}
    for clave, normalizar in pieza.normalizar_opcion.items():
        if clave in resultado:
            resultado[clave] = normalizar(resultado[clave])
    return resultado


def campos_reservados(pieza: Pieza, nombre: Nombre) -> dict[str, str]:
    return pieza.campos_reservados(nombre) if pieza.campos_reservados else {}


def preparar_campos(stack: Stack, pieza: Pieza, nombre: Nombre, textos: list[str]) -> list[Campo]:
    reservados = campos_reservados(pieza, nombre)
    campos = [parsear_campo(t, stack.tipos, reservados) for t in textos]
    validar_campos(campos)
    if pieza.usa_campos and not campos:
        raise AndamioError(
            f"Indicá al menos un campo para '{pieza.clave}'.",
            f"Ejemplo: {consola.programa()} nuevo {pieza.clave} {pieza.ejemplo}",
        )
    if campos and not pieza.usa_campos:
        raise AndamioError(
            f"La pieza '{pieza.clave}' no lleva campos.", f"Ejemplo: {consola.programa()} nuevo {pieza.clave} {pieza.ejemplo}"
        )
    return campos


def generar_pieza(sol: Solicitud, simular: bool = False, confirmar: bool = False) -> int:
    consola.escribir(f"Se usará: {consola.color(describir_nombre(sol.pieza, sol.nombre), 'negrita')}")
    if sol.campos:
        consola.escribir("Campos: " + ", ".join(f"{c.nombre} ({c.tipo})" for c in sol.campos))
    _, personalizada = ubicar_plantilla(sol.stack, sol.pieza, sol.raiz, sol.variante)
    if personalizada:
        consola.aviso(f"Se usan tus plantillas de .andamio/plantillas/{sol.stack.clave}/{sol.pieza.clave}/")
    plan = planificar_pieza(sol)
    if not _cerrar(plan, simular, confirmar, "¿Generar estos archivos?"):
        return 0
    if confirmar:
        # En el menú, las opciones de "después" (ej.: migrar) se preguntan al final.
        for opcion, pregunta in sol.pieza.confirmaciones.items():
            if opcion not in sol.opciones:
                consola.escribir()
                sol.opciones[opcion] = consola.confirmar(pregunta, defecto=True)
    if sol.pieza.despues:
        sol.pieza.despues(sol)
    lectura.mostrar(lectura.orden_de_lectura(sol.pieza.lectura, sol.contexto), lectura.marcas_del_plan(plan))
    mostrar_pasos(pasos_pieza(sol))
    return 0


def nuevo(
    cwd: Path,
    clave_pieza: str,
    texto_nombre: str | None,
    textos_campos: list[str],
    plural: str | None = None,
    opciones: dict[str, Any] | None = None,
    simular: bool = False,
) -> int:
    stack, raiz = proyecto_actual(cwd)
    pieza = pieza_por_clave(stack, clave_pieza)
    opciones = preparar_opciones(pieza, opciones or {})
    if not texto_nombre:
        if not pieza.nombre_defecto:
            raise AndamioError(
                f"Falta el nombre de '{pieza.clave}'.",
                f"Ejemplo: {consola.programa()} nuevo {pieza.clave} {pieza.ejemplo}",
            )
        texto_nombre = pieza.nombre_defecto
    if plural and not pieza.usa_plural:
        raise AndamioError(f"La pieza '{pieza.clave}' no usa plural; sacá la opción --plural.")
    nombre = preparar_nombre(stack, pieza, raiz, texto_nombre, plural)
    if pieza.usa_plural and not plural and parece_plural(nombre.palabras):
        raise AndamioError(
            f"'{texto_nombre}' parece estar en plural. Los nombres van en singular (ej: 'producto', no 'productos').",
            "Si de verdad es singular (como 'país'), indicá el plural con --plural. Ejemplo: --plural paises",
        )
    campos = preparar_campos(stack, pieza, nombre, textos_campos)
    sol = Solicitud(stack, pieza, raiz, nombre, campos, opciones, variante=variante_del_proyecto(stack, raiz))
    return generar_pieza(sol, simular=simular)


# --- info ---------------------------------------------------------------------


def info(cwd: Path) -> int:
    stack, raiz = proyecto_actual(cwd)
    variante = nombre_variante(stack, variante_del_proyecto(stack, raiz))
    consola.titulo(f"Proyecto {stack.titulo}" + (f" ({variante})" if variante else ""))
    consola.escribir(f"Carpeta: {raiz}")
    consola.escribir()
    consola.titulo("Piezas que podés generar:")
    ancho = max(len(c) for c in stack.piezas)
    for clave, pieza in stack.piezas.items():
        consola.escribir(f"  {clave.ljust(ancho)}  {pieza.descripcion}")
        consola.escribir(consola.color(f"  {' ' * ancho}  {consola.programa()} nuevo {clave} {pieza.ejemplo}".rstrip(), "gris"))
    if any(p.usa_campos for p in stack.piezas.values()):
        consola.escribir()
        consola.titulo("Tipos de campo:")
        ancho_tipo = max(len(t) for t in stack.tipos)
        for tipo, descripcion in stack.tipos.items():
            consola.escribir(f"  {tipo.ljust(ancho_tipo)}  {descripcion}")
    return 0
