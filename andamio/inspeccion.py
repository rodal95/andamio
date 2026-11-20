"""Comandos que miran el proyecto: `pendientes` e `init`.

- `pendientes` busca las marcas TODO(logica) que deja andamio en el código generado: son
  los lugares donde va la lógica propia (validaciones, reglas de negocio, cálculos).
- `init` prepara un proyecto que ya existe (aunque no lo haya creado andamio): dice qué
  puntos de conexión tiene y cuáles faltan, y crea andamio.json.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from andamio import acciones, stacks
from andamio.nucleo import ajustes, consola
from andamio.nucleo.campos import parsear_campo
from andamio.nucleo.deteccion import buscar_proyecto
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.generador import contexto_pieza, nombre_para_pieza, nombre_variante, resolver_variante
from andamio.nucleo.insercion import linea_marcador
from andamio.nucleo.lectura import MARCA_LOGICA, Pendiente, buscar_marcas
from andamio.nucleo.motor import renderizar, renderizar_ruta
from andamio.nucleo.plan import Plan
from andamio.stacks.base import Pieza, Solicitud, Stack

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


# --- init -------------------------------------------------------------------------------


@dataclass
class PuntoDeConexion:
    """Un marcador (andamio:<clave>) donde andamio agrega líneas: imports, rutas, enlaces."""

    archivo: str
    marcador: str
    linea: str  # la línea del marcador, como hay que pegarla
    ubicacion: str  # dónde va, en palabras
    piezas: list[str] = field(default_factory=list)
    estado: str = ""  # "ok", "falta el marcador" o "falta el archivo"


def _contexto_de_ejemplo(stack: Stack, pieza: Pieza, raiz: Path, variante: str) -> dict[str, str]:
    """Los marcadores de la pieza con su ejemplo, para saber las rutas de sus conexiones."""
    nombre_texto, *campos_texto = pieza.ejemplo.split() or [pieza.nombre_defecto or "ejemplo"]
    try:
        nombre = nombre_para_pieza(pieza, nombre_texto)
        campos = [parsear_campo(c, stack.tipos) for c in campos_texto]
        return contexto_pieza(Solicitud(stack, pieza, raiz, nombre, campos, variante=variante))
    except (AndamioError, OSError, LookupError, ValueError):
        return dict(stack.marcadores_variante.get(variante, {}))


def puntos_de_conexion(stack: Stack, raiz: Path, variante: str) -> list[PuntoDeConexion]:
    conexiones = ajustes.de_proyecto(raiz).conexiones
    puntos: dict[tuple[str, str], PuntoDeConexion] = {}
    for clave, pieza in stack.piezas.items():
        contexto = _contexto_de_ejemplo(stack, pieza, raiz, variante)
        for ins in pieza.inserciones:
            if not ins.marcador:
                continue
            try:
                archivo = conexiones.get(ins.marcador) or renderizar_ruta(tuple(ins.archivo.split("/")), contexto).as_posix()
                ubicacion = renderizar(ins.ubicacion, contexto) if ins.ubicacion else "en el lugar que corresponda"
            except AndamioError:
                continue  # la ruta depende del nombre de la pieza: no es un punto fijo del proyecto
            punto = puntos.setdefault(
                (archivo, ins.marcador),
                PuntoDeConexion(archivo, ins.marcador, linea_marcador(ins.marcador, ins.comentario), ubicacion),
            )
            if clave not in punto.piezas:
                punto.piezas.append(clave)
    for punto in puntos.values():
        ruta = raiz / PurePosixPath(punto.archivo)
        if not ruta.is_file():
            punto.estado = "falta el archivo"
            continue
        try:
            texto = ruta.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            texto = ""
        punto.estado = "ok" if re.search(rf"andamio:{re.escape(punto.marcador)}\b", texto) else "falta el marcador"
    return sorted(puntos.values(), key=lambda p: (p.archivo, p.marcador))


def _mostrar_puntos(puntos: list[PuntoDeConexion]) -> None:
    if not puntos:
        consola.escribir("Las piezas de este tipo de proyecto no se conectan con otros archivos.")
        return
    consola.titulo("Puntos de conexión (donde andamio agrega imports, rutas y enlaces):")
    ancho = max(len(f"{p.archivo}  andamio:{p.marcador}") for p in puntos)
    for punto in puntos:
        etiqueta = consola.color("ok   ", "verde") if punto.estado == "ok" else consola.color("falta", "amarillo")
        donde = f"{punto.archivo}  andamio:{punto.marcador}".ljust(ancho)
        consola.escribir(f"  {etiqueta}  {donde}  " + consola.color(f"({', '.join(punto.piezas)})", "gris"))
        if punto.estado == "falta el marcador":
            consola.escribir(f"         Pegá esta línea {punto.ubicacion}:")
            consola.escribir("           " + consola.color(punto.linea, "cian"))
        elif punto.estado == "falta el archivo":
            consola.escribir("         El archivo no existe.")
    if any(p.estado != "ok" for p in puntos):
        consola.escribir()
        consola.escribir(
            "Sin esos marcadores, andamio igual genera los archivos de cada pieza y te muestra qué pegar a mano."
        )
        consola.escribir(
            f'Si un punto está en otro archivo, indicalo en {ajustes.ARCHIVO}: "conexiones": {{"rutas": "src/router.tsx"}}'
        )


def init(cwd: Path, tipo: str | None = None, variante: str | None = None, simular: bool = False) -> int:
    if tipo:
        stack, raiz = acciones.stack_por_clave(tipo), cwd
    else:
        encontrado = buscar_proyecto(cwd)
        if encontrado is None:
            claves = ", ".join(s.clave for s in stacks.ORDEN_MENU)
            raise AndamioError(
                f"No reconozco el tipo de proyecto de {cwd}.",
                f"Indicalo: {consola.programa()} init <tipo>   (tipos: {claves})",
            )
        stack, raiz = encontrado
    if variante is None and stack.variantes and stack.detectar_variante:
        variante = stack.detectar_variante(raiz)
    variante = resolver_variante(stack, variante)
    nombre = nombre_variante(stack, variante)
    consola.titulo(f"Proyecto {stack.titulo}" + (f" ({nombre})" if nombre else "") + f" en {raiz}")
    consola.escribir()
    _mostrar_puntos(puntos_de_conexion(stack, raiz, variante))
    consola.escribir()
    if (raiz / ajustes.ARCHIVO).exists():
        ajustes.leer(raiz)  # avisa si tiene un error
        consola.aviso(f"Ya existe {ajustes.ARCHIVO}: no se modifica.")
        return 0
    plan = Plan(raiz)
    plan.crear(ajustes.ARCHIVO, ajustes.texto(stack.clave, variante))
    if simular:
        plan.mostrar()
        consola.escribir()
        consola.escribir(consola.color("Simulación: no se creó ningún archivo.", "amarillo", "negrita"))
        return 0
    plan.aplicar()
    consola.exito(f"Se creó {ajustes.ARCHIVO}: desde ahora andamio usa esta configuración en esta carpeta.")
    consola.escribir(f"Para ver qué podés generar: {consola.comando(consola.programa() + ' info')}")
    return 0
