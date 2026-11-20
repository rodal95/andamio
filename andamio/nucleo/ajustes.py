"""andamio.json: la configuración (opcional) de un proyecto.

Sin este archivo, andamio funciona como siempre: detecta el tipo de proyecto por sus
archivos. Con él se puede fijar lo que no se puede detectar o cambiar lo de siempre:

    {
      "version": 1,
      "stack": "react",
      "variante": "ts",
      "guia": true,
      "plantillas": ".andamio/plantillas",
      "conexiones": { "rutas": "src/router/AppRouter.tsx" }
    }

- stack: el tipo de proyecto (como en `crear`). Si está, la carpeta de andamio.json es la
  raíz del proyecto, aunque los archivos no sean los de siempre.
- variante: ts o js (en los stacks que tienen variantes).
- guia: false para generar sin los comentarios que explican el código (como --sin-guia).
- plantillas: carpeta de las plantillas propias (por defecto, .andamio/plantillas).
- conexiones: en qué archivo están los puntos de conexión (los marcadores
  `andamio:<clave>`), si no están en el archivo de siempre. Ej.: las rutas de React en
  src/router/AppRouter.tsx en lugar de src/App.tsx.

Lo que se indique al ejecutar (ej.: --sin-guia) tiene prioridad sobre andamio.json.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from andamio.nucleo.errores import AndamioError

ARCHIVO = "andamio.json"
VERSION = 1
CARPETA_PLANTILLAS = ".andamio/plantillas"

_CLAVES = {
    "version": "versión del formato del archivo (1)",
    "stack": "tipo de proyecto (django, react, ...)",
    "variante": "ts o js",
    "guia": "true o false",
    "plantillas": "carpeta de las plantillas propias",
    "conexiones": 'archivo de cada punto de conexión: {"rutas": "src/router.tsx"}',
}


@dataclass(frozen=True)
class Ajustes:
    stack: str | None = None
    variante: str | None = None
    guia: bool | None = None
    plantillas: str = CARPETA_PLANTILLAS
    conexiones: dict[str, str] = field(default_factory=dict)


def _error(mensaje: str, sugerencia: str | None = None) -> AndamioError:
    return AndamioError(f"{ARCHIVO}: {mensaje}", sugerencia or f"Revisá {ARCHIVO}, en la carpeta del proyecto.")


def _ruta_relativa(valor: object, que: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise _error(f"{que} tiene que ser una ruta (texto), por ejemplo \"src/App.tsx\".")
    ruta = PurePosixPath(valor.strip().replace("\\", "/"))
    if ruta.is_absolute() or ".." in ruta.parts or ":" in valor:
        raise _error(f"{que} tiene que ser una ruta dentro del proyecto, relativa a andamio.json: '{valor}'.")
    return ruta.as_posix()


def desde_texto(texto: str) -> Ajustes:
    """Lee y valida el contenido de andamio.json."""
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise _error(
            f"no es un JSON válido (línea {e.lineno}, columna {e.colno}: {e.msg}).",
            "Fijate que las claves y los textos vayan entre comillas dobles y que no sobre una coma al final.",
        ) from e
    if not isinstance(datos, dict):
        raise _error("tiene que ser un objeto: { ... }.")
    desconocidas = sorted(set(datos) - set(_CLAVES))
    if desconocidas:
        validas = "\n".join(f"  {clave}: {descripcion}" for clave, descripcion in _CLAVES.items())
        raise _error(f"no conozco {', '.join(repr(c) for c in desconocidas)}.", f"Las claves que se pueden usar son:\n{validas}")
    version = datos.get("version", VERSION)
    if version != VERSION:
        raise _error(f"la versión {version!r} no existe (esta versión de andamio usa {VERSION}).")
    stack = datos.get("stack")
    if stack is not None and (not isinstance(stack, str) or not stack.strip()):
        raise _error('"stack" tiene que ser un texto, por ejemplo "django".')
    variante = datos.get("variante")
    if variante is not None and variante not in ("ts", "js"):
        raise _error('"variante" tiene que ser "ts" o "js".')
    guia = datos.get("guia")
    if guia is not None and not isinstance(guia, bool):
        raise _error('"guia" tiene que ser true o false (sin comillas).')
    plantillas = _ruta_relativa(datos.get("plantillas", CARPETA_PLANTILLAS), '"plantillas"')
    conexiones = datos.get("conexiones", {})
    if not isinstance(conexiones, dict):
        raise _error('"conexiones" tiene que ser un objeto: {"rutas": "src/router.tsx"}.')
    return Ajustes(
        stack=stack.strip() if stack else None,
        variante=variante,
        guia=guia,
        plantillas=plantillas,
        conexiones={str(clave): _ruta_relativa(ruta, f'"conexiones.{clave}"') for clave, ruta in conexiones.items()},
    )


def leer(raiz: Path) -> Ajustes | None:
    """Los ajustes de andamio.json en `raiz`, o None si no hay archivo."""
    archivo = raiz / ARCHIVO
    if not archivo.is_file():
        return None
    try:
        texto = archivo.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        raise _error(f"no se pudo leer ({e}).") from e
    return desde_texto(texto)


def de_proyecto(raiz: Path) -> Ajustes:
    """Los ajustes del proyecto (los de siempre si no hay andamio.json)."""
    return leer(raiz) or Ajustes()


def guia(raiz: Path, pedida: bool | None = None) -> bool:
    """Si se generan los comentarios de guía: lo pedido al ejecutar, o andamio.json, o sí."""
    if pedida is not None:
        return pedida
    configurada = de_proyecto(raiz).guia
    return True if configurada is None else configurada


def texto(stack: str, variante: str = "", guia_activada: bool = True, conexiones: dict[str, str] | None = None) -> str:
    """El contenido de un andamio.json nuevo."""
    datos: dict[str, object] = {"version": VERSION, "stack": stack}
    if variante:
        datos["variante"] = variante
    datos["guia"] = guia_activada
    datos["plantillas"] = CARPETA_PLANTILLAS
    datos["conexiones"] = conexiones or {}
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"
