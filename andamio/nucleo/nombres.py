"""Normalización y validación de los nombres que escribe el alumno.

"Línea venta", "linea-venta" o "LineaVenta" se convierten en la misma lista de
palabras (["linea", "venta"]) y de ahí se derivan todas las formas:
LineaVenta, linea_venta, lineaVenta, linea-venta, y sus plurales.
"""

from __future__ import annotations

import keyword
import re
import unicodedata
from dataclasses import dataclass

from andamio.nucleo.errores import AndamioError

RESERVADAS_PYTHON = frozenset(keyword.kwlist)

RESERVADAS_JS = frozenset(
    """
    arguments await break case catch class const continue debugger default delete do
    else enum eval export extends false finally for function if implements import in
    instanceof interface let new null package private protected public return static
    super switch this throw true try typeof var void while with yield
    """.split()
)

# Nombres de campo que no se pueden usar en ningún stack.
CAMPOS_RESERVADOS = {
    "id": "el campo 'id' se crea automáticamente",
    "pk": "'pk' es un alias de 'id' en Django",
    "creado": "andamio agrega el campo 'creado' automáticamente",
    "actualizado": "andamio agrega el campo 'actualizado' automáticamente",
}

_TROZO = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+[0-9]*|[A-Z]+[0-9]*|[0-9]+")
_SEPARADORES = re.compile(r"[\s_\-]+")


def quitar_tildes(texto: str) -> str:
    """Quita tildes y diéresis. La ñ se convierte en "ni" (año -> anio), la convención habitual."""
    texto = re.sub(r"Ñ(?=[A-Z]|$)", "NI", texto)
    texto = texto.replace("Ñ", "Ni").replace("ñ", "ni")
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def separar_palabras(texto: str, que: str = "El nombre") -> list[str]:
    """Convierte lo que escribió el alumno en una lista de palabras en minúscula y sin tildes."""
    limpio = quitar_tildes(texto.strip())
    if not limpio:
        raise AndamioError(f"{que} está vacío.")
    invalidos = sorted({c for c in limpio if not (c.isascii() and (c.isalnum() or c in " -_"))})
    if invalidos:
        raise AndamioError(
            f"{que} '{texto}' tiene caracteres que no se pueden usar: {' '.join(invalidos)}",
            "Usá solo letras, números, espacios y guiones.",
        )
    palabras: list[str] = []
    for trozo in _SEPARADORES.split(limpio):
        palabras.extend(p.lower() for p in _TROZO.findall(trozo))
    if not palabras:
        raise AndamioError(f"{que} '{texto}' no tiene letras.")
    if palabras[0][0].isdigit():
        raise AndamioError(f"{que} '{texto}' no puede empezar con un número.")
    return palabras


# --- Formas -----------------------------------------------------------------


def snake(palabras: list[str] | tuple[str, ...]) -> str:
    return "_".join(palabras)


def pascal(palabras: list[str] | tuple[str, ...]) -> str:
    return "".join(p[0].upper() + p[1:] for p in palabras)


def camel(palabras: list[str] | tuple[str, ...]) -> str:
    texto = pascal(palabras)
    return texto[0].lower() + texto[1:]


def kebab(palabras: list[str] | tuple[str, ...]) -> str:
    return "-".join(palabras)


def titulo(palabras: list[str] | tuple[str, ...]) -> str:
    texto = " ".join(palabras)
    return texto[0].upper() + texto[1:]


# --- Plural -----------------------------------------------------------------


def pluralizar_palabra(palabra: str) -> str:
    """Reglas básicas del castellano: vocal + s, z -> ces, consonante + es."""
    if palabra[-1] in "aeiou" or palabra[-1].isdigit():
        return palabra + "s"
    if palabra[-1] == "z":
        return palabra[:-1] + "ces"
    return palabra + "es"


def pluralizar(palabras: list[str] | tuple[str, ...]) -> list[str]:
    """Pluraliza la primera palabra, que en castellano es el núcleo: línea venta -> líneas venta."""
    return [pluralizar_palabra(palabras[0]), *palabras[1:]]


def parece_plural(palabras: list[str] | tuple[str, ...]) -> bool:
    primera = palabras[0]
    return len(primera) > 3 and primera.endswith("s")


# --- Nombre completo --------------------------------------------------------


@dataclass(frozen=True)
class Nombre:
    """Un nombre ya normalizado, con todas sus formas."""

    palabras: tuple[str, ...]
    plural_palabras: tuple[str, ...]

    @classmethod
    def desde_texto(cls, texto: str, plural: str | None = None) -> Nombre:
        palabras = separar_palabras(texto)
        plural_palabras = separar_palabras(plural, "El plural") if plural else pluralizar(palabras)
        return cls(tuple(palabras), tuple(plural_palabras))

    @classmethod
    def desde_palabras(cls, palabras: list[str], plural: list[str] | None = None) -> Nombre:
        return cls(tuple(palabras), tuple(plural or pluralizar(palabras)))

    def con_plural(self, plural: str) -> Nombre:
        return Nombre(self.palabras, tuple(separar_palabras(plural, "El plural")))

    @property
    def snake(self) -> str:
        return snake(self.palabras)

    @property
    def pascal(self) -> str:
        return pascal(self.palabras)

    @property
    def camel(self) -> str:
        return camel(self.palabras)

    @property
    def kebab(self) -> str:
        return kebab(self.palabras)

    @property
    def plural(self) -> str:
        return snake(self.plural_palabras)

    def forma(self, nombre: str) -> str:
        """Devuelve una forma por nombre: 'pascal', 'snake', 'camel', 'kebab'."""
        return getattr(self, nombre)

    def marcadores(self) -> dict[str, str]:
        p, pl = self.palabras, self.plural_palabras
        return {
            "Nombre": pascal(p),
            "nombre": snake(p),
            "nombreCamel": camel(p),
            "nombreKebab": kebab(p),
            "nombreTitulo": titulo(p),
            "Plural": pascal(pl),
            "plural": snake(pl),
            "pluralCamel": camel(pl),
            "pluralKebab": kebab(pl),
            "titulo": titulo(pl),
        }


MARCADORES_NOMBRE = {
    "Nombre": "nombre en PascalCase",
    "nombre": "nombre en snake_case",
    "nombreCamel": "nombre en camelCase",
    "nombreKebab": "nombre en kebab-case",
    "nombreTitulo": "nombre para mostrar",
    "Plural": "plural en PascalCase",
    "plural": "plural en snake_case",
    "pluralCamel": "plural en camelCase",
    "pluralKebab": "plural en kebab-case",
    "titulo": "plural para mostrar (títulos y menús)",
}


# Windows no deja crear archivos ni carpetas con estos nombres (aunque tengan extensión:
# "con.py" o "Aux.tsx" fallan).
RESERVADAS_WINDOWS = frozenset(
    {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
)


def _motivo_reservado(forma: str) -> str | None:
    if forma in RESERVADAS_PYTHON:
        return "es una palabra reservada de Python"
    if forma in RESERVADAS_JS:
        return "es una palabra reservada de JavaScript"
    if forma.lower() in RESERVADAS_WINDOWS:
        return "Windows no deja crear archivos con ese nombre"
    return None


def formas_identificador(nombre: Nombre) -> list[str]:
    """Las formas del nombre que el código generado usa como identificadores."""
    p, pl = nombre.palabras, nombre.plural_palabras
    return list(dict.fromkeys([snake(p), camel(p), pascal(p), snake(pl), camel(pl), pascal(pl)]))


def validar_nombre(nombre: Nombre, reservados: dict[str, str] | None = None) -> None:
    """Rechaza palabras reservadas y nombres que chocan con algo que ya existe."""
    reservados = reservados or {}
    for forma in [*formas_identificador(nombre), nombre.kebab, kebab(nombre.plural_palabras)]:
        motivo = _motivo_reservado(forma) or reservados.get(forma)
        if motivo:
            raise AndamioError(f"No se puede usar '{forma}': {motivo}.", "Elegí otro nombre.")


def validar_nombre_carpeta(texto: str) -> None:
    """Un nombre de carpeta que Windows no acepta (con, aux, nul...)."""
    if texto.lower() in RESERVADAS_WINDOWS:
        raise AndamioError(f"No se puede usar '{texto}': Windows no deja crear carpetas con ese nombre.", "Elegí otro nombre.")


def validar_nombre_campo(texto: str, reservados: dict[str, str] | None = None) -> str:
    """Normaliza el nombre de un campo a snake_case y lo valida."""
    nombre = snake(separar_palabras(texto, "El nombre del campo"))
    motivo = (
        _motivo_reservado(nombre)
        or _motivo_reservado(camel(nombre.split("_")))
        or CAMPOS_RESERVADOS.get(nombre)
        or (reservados or {}).get(nombre)
    )
    if motivo:
        raise AndamioError(f"No se puede usar el campo '{nombre}': {motivo}.", "Elegí otro nombre de campo.")
    return nombre
