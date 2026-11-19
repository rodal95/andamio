"""Piezas y ayudas compartidas por los stacks de JavaScript (react y react-native)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from andamio.nucleo.deteccion import dependencias_npm
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre, kebab, separar_palabras
from andamio.stacks.base import Solicitud
from andamio.stacks.django import TIPOS as TIPOS_API

# Los servicios usan los mismos tipos que el recurso de Django, para que el
# mismo comando sirva en los dos lados: nombre:str precio:decimal ...
TIPOS = TIPOS_API

_TIPOS_TS = {
    "str": "string",
    "text": "string",
    "int": "number",
    "decimal": "number",
    "float": "number",
    "bool": "boolean",
    "date": "string",
    "datetime": "string",
    "email": "string",
}

_COMENTARIOS_TS = {
    "decimal": "  // Django lo envía como número (COERCE_DECIMAL_TO_STRING = False)",
    "date": '  // fecha: "2025-03-15"',
    "datetime": '  // fecha y hora: "2025-03-15T10:30:00Z"',
}

_COMENTARIOS_JSDOC = {
    "decimal": "número con 2 decimales",
    "date": 'fecha: "2025-03-15"',
    "datetime": 'fecha y hora: "2025-03-15T10:30:00Z"',
}

# --- Variantes: TypeScript y JavaScript -------------------------------------------------

VARIANTES = {"ts": "TypeScript", "js": "JavaScript"}

MARCADORES_VARIANTE = {
    "ts": {"ext": "ts", "extx": "tsx"},
    "js": {"ext": "js", "extx": "jsx"},
}

MARCADORES_EXTENSION = {
    "ext": "extensión de los archivos de código: ts o js",
    "extx": "extensión de los componentes: tsx o jsx",
}


def detectar_variante(raiz: Path) -> str:
    """TypeScript si el proyecto tiene tsconfig.json o la dependencia typescript."""
    if (raiz / "tsconfig.json").is_file() or "typescript" in dependencias_npm(raiz):
        return "ts"
    return "js"


MARCADORES_SERVICIO = {
    **MARCADORES_EXTENSION,
    "campos_ts": "una línea por campo de la interfaz (TypeScript): precio: number;",
    "campos_jsdoc": "una línea por campo del comentario JSDoc (JavaScript): * @property {number} precio",
}


def contexto_servicio(sol: Solicitud) -> dict[str, str]:
    # Los campos quedan en snake_case, igual que en el JSON que devuelve Django.
    lineas_ts = [f"{c.nombre}: {_TIPOS_TS[c.tipo]};{_COMENTARIOS_TS.get(c.tipo, '')}" for c in sol.campos]
    lineas_jsdoc = [
        f"* @property {{{_TIPOS_TS[c.tipo]}}} {c.nombre}" + (f" {_COMENTARIOS_JSDOC[c.tipo]}" if c.tipo in _COMENTARIOS_JSDOC else "")
        for c in sol.campos
    ]
    return {"campos_ts": "\n".join(lineas_ts), "campos_jsdoc": "\n".join(lineas_jsdoc)}


def detectar_dependencias(*paquetes: str) -> Callable[[Path], bool]:
    def detectar(raiz: Path) -> bool:
        if not (raiz / "package.json").is_file():
            return False
        return set(paquetes) <= dependencias_npm(raiz)

    return detectar


# --- Ajustes de nombres -------------------------------------------------------------


def sin_prefijo_use(palabras: list[str]) -> list[str]:
    """"useContador" y "contador" generan el mismo hook: useContador."""
    return palabras[1:] if palabras and palabras[0] == "use" else palabras


def sin_sufijo(*sufijos: str) -> Callable[[list[str]], list[str]]:
    """"ProductosPage" y "Productos" generan la misma página: ProductosPage."""

    def ajustar(palabras: list[str]) -> list[str]:
        return palabras[:-1] if len(palabras) > 1 and palabras[-1] in sufijos else palabras

    return ajustar


_HOOKS_DE_REACT = {
    "useState", "useEffect", "useRef", "useMemo", "useCallback", "useContext", "useReducer", "useId",
    "useTransition", "useDeferredValue", "useLayoutEffect", "useInsertionEffect", "useImperativeHandle",
    "useSyncExternalStore", "useDebugValue", "useActionState", "useOptimistic", "useFormStatus",
}  # fmt: skip

_COMPONENTES_OCUPADOS = {"App", "React", "Fragment", "StrictMode", "Suspense", "Profiler"}


def validar_hook(raiz: Path, nombre: Nombre) -> None:
    hook = f"use{nombre.pascal}"
    if hook in _HOOKS_DE_REACT:
        raise AndamioError(f"'{hook}' ya existe en React; si creás otro con ese nombre se confunden.", "Elegí otro nombre.")


def validar_componente(raiz: Path, nombre: Nombre) -> None:
    if nombre.pascal in _COMPONENTES_OCUPADOS:
        raise AndamioError(f"'{nombre.pascal}' ya lo usa React o el proyecto.", "Elegí otro nombre para el componente.")


# --- Carpeta de pantallas (Expo Router) ----------------------------------------------


def normalizar_carpeta(texto: str) -> str:
    """"Productos" -> "productos"; "(Tabs)" -> "(tabs)" (grupo de Expo Router); admite "a/b"."""
    partes: list[str] = []
    for parte in re.split(r"[\\/]+", texto.strip()):
        if not parte:
            continue
        grupo = parte.startswith("(") and parte.endswith(")")
        interior = parte[1:-1] if grupo else parte
        normal = kebab(separar_palabras(interior, "La carpeta"))
        partes.append(f"({normal})" if grupo else normal)
    if not partes:
        raise AndamioError("La carpeta está vacía.")
    return "/".join(partes)


def contexto_pantalla(sol: Solicitud) -> dict[str, str]:
    carpeta = sol.opciones.get("carpeta", "")
    archivo = sol.nombre.kebab
    ruta = f"{carpeta}/{archivo}" if carpeta else archivo
    # Los grupos "(tabs)" no forman parte de la URL, y "index" es la ruta de la carpeta.
    segmentos = [p for p in ruta.split("/") if not p.startswith("(")]
    if segmentos and segmentos[-1] == "index":
        segmentos.pop()
    return {"ruta_pantalla": ruta, "url_pantalla": "/" + "/".join(segmentos)}


MARCADORES_PANTALLA = {
    **MARCADORES_EXTENSION,
    "ruta_pantalla": "archivo dentro de app/, sin extensión: productos/detalle-producto",
    "url_pantalla": "ruta para navegar: /productos/detalle-producto",
}
