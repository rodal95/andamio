"""Menú interactivo: lo que se ejecuta al escribir solo `andamio`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from andamio import __version__, acciones, stacks
from andamio.nucleo import ajustes, consola
from andamio.nucleo.campos import Campo, validar_tipo
from andamio.nucleo.deteccion import buscar_proyecto
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.generador import (
    carpeta_proyecto,
    describir_nombre,
    en_la_carpeta_actual,
    nombre_variante,
    validar_carpeta_actual,
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
        if en_la_carpeta_actual(texto):
            validar_carpeta_actual(cwd)
            return texto
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
    texto = consola.preguntar("Nombre del proyecto (o . para crearlo en esta carpeta)", validar=validar, ejemplo=stack.ejemplo_proyecto)
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
    if pieza.usa_campos and not pieza.define_campos:
        campos = _pedir_nombres(pieza)
    else:
        campos = _pedir_campos(stack, acciones.campos_reservados(pieza, nombre)) if pieza.usa_campos else []
    consola.escribir()
    sol = Solicitud(stack, pieza, raiz, nombre, campos, extras, variante=variante, guia=ajustes.guia(raiz))
    return acciones.generar_pieza(sol, confirmar=True)


def _pedir_nombre(stack: Stack, pieza: Pieza, raiz: Path) -> Nombre:
    if pieza.nombre_defecto and pieza.pregunta_nombre:
        nombre = consola.preguntar(
            pieza.pregunta_nombre,
            validar=lambda t: acciones.preparar_nombre(stack, pieza, raiz, t or pieza.nombre_defecto, None),
            permitir_vacio=True,
        ) or acciones.preparar_nombre(stack, pieza, raiz, pieza.nombre_defecto, None)
        consola.escribir(f"Se usará: {consola.color(describir_nombre(pieza, nombre), 'negrita')}")
        return nombre
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
    if "protegido" in pieza.opciones and pieza.clave in ("pagina", "pantalla"):
        extras["protegido"] = consola.confirmar("¿Solo para quien ingresó? (necesita el login: nuevo login)", defecto=False)
    elif "protegido" in pieza.opciones:
        extras["protegido"] = consola.confirmar(
            "¿Proteger el recurso? (solo usuarios con login pueden crear, modificar y eliminar)", defecto=False
        )
    if "obligatorio" in pieza.opciones:
        extras["obligatorio"] = consola.confirmar(
            "¿Login obligatorio para todo? (sin ingresar no se puede usar nada, salvo ingresar y registrarse)", defecto=False
        )
    if "sin_registro" in pieza.opciones:
        extras["sin_registro"] = not consola.confirmar("¿También la página para crear una cuenta (/registro)?", defecto=True)
    if "solo_lectura" in pieza.opciones and not extras.get("protegido"):
        extras["solo_lectura"] = consola.confirmar(
            "¿Solo lectura? (la API solo lista y muestra; los datos se cargan desde /admin/)", defecto=False
        )
    if "modo" in pieza.opciones:
        extras["modo"] = consola.elegir(
            "¿Modo del tema?",
            [("auto", "auto: claro u oscuro según el sistema (recomendado)"), ("claro", "siempre claro"), ("oscuro", "siempre oscuro")],
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
    if "datos" in pieza.opciones:
        datos = consola.preguntar(
            "¿Muestra datos de la API? Escribí el nombre del servicio (Enter para no usar datos)",
            validar=pieza.normalizar_opcion.get("datos"),
            permitir_vacio=True,
            ejemplo="producto",
        )
        if datos:
            extras["datos"] = datos
            que = consola.elegir(
                "¿Qué hace con esos datos?",
                [
                    ("lista", "muestra la lista (listar)"),
                    ("uno", "muestra uno solo, con el id en la ruta (obtener)"),
                    ("form", "el formulario para crear y editar (crear, actualizar); si el servicio solo tiene crear, solo envía"),
                ],
            )
            extras["uno"], extras["form"] = que == "uno", que == "form"
    if "solo" in pieza.opciones:
        solo = consola.preguntar(
            "¿Solo algunas funciones? (Enter para todas: listar, obtener, crear, actualizar, eliminar)",
            validar=pieza.normalizar_opcion.get("solo"),
            permitir_vacio=True,
            ejemplo="crear, o listar,obtener",
        )
        if solo:
            extras["solo"] = solo
    return extras


def _pedir_nombres(pieza: Pieza) -> list[Campo]:
    """Para piezas como busqueda o accion: solo nombres (de campos o de acciones), sin tipo."""
    que = "acción" if pieza.clave == "accion" else "campo"
    consola.escribir()
    consola.escribir(consola.color(f"Escribí un {que} por vez. Cuando termines, apretá Enter sin escribir nada.", "gris"))
    nombres: list[Campo] = []
    while True:
        nombre = consola.preguntar(f"Nombre del {que} (Enter para terminar)", validar=validar_nombre_campo, permitir_vacio=True)
        if not nombre:
            if nombres:
                return nombres
            consola.escribir(consola.color("  Escribí al menos uno.", "amarillo"))
            continue
        nombres.append(Campo(nombre, "str"))


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
