"""Entrada y salida por consola: colores, mensajes y preguntas al alumno.

Todo lo que se muestra pasa por este módulo, así el estilo es uniforme.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, Sequence, TypeVar

from andamio.nucleo.errores import AndamioError, Cancelado

T = TypeVar("T")

_CODIGOS = {
    "negrita": "1",
    "rojo": "31",
    "verde": "32",
    "amarillo": "33",
    "azul": "34",
    "cian": "36",
    "gris": "90",
}

_usar_color: bool | None = None


def configurar_salida() -> None:
    """Evita que un carácter no representable corte el programa (consola de Windows redirigida)."""
    for flujo in (sys.stdout, sys.stderr):
        reconfigurar = getattr(flujo, "reconfigure", None)
        if reconfigurar is not None:
            try:
                reconfigurar(errors="replace")
            except (ValueError, OSError):
                pass


def _detectar_color() -> bool:
    if "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb":
        return False
    esta_en_terminal = getattr(sys.stdout, "isatty", None)
    if esta_en_terminal is None or not esta_en_terminal():
        return False
    if os.name == "nt":
        # En Windows 10+ esta llamada vacía habilita las secuencias de color ANSI.
        os.system("")
    return True


def usar_color() -> bool:
    global _usar_color
    if _usar_color is None:
        _usar_color = _detectar_color()
    return _usar_color


def color(texto: str, *estilos: str) -> str:
    if not usar_color() or not estilos:
        return texto
    codigos = ";".join(_CODIGOS[e] for e in estilos)
    return f"\033[{codigos}m{texto}\033[0m"


def programa() -> str:
    """Cómo se ejecuta andamio, para mostrarlo en los mensajes.

    Siempre con Python adelante, porque funciona en cualquier PC aunque el comando
    `andamio` solo no esté en el PATH: `python -m andamio`, o `python andamio.pyz`
    si se usa el archivo .pyz sin instalar.
    """
    origen = Path(sys.argv[0]) if sys.argv and sys.argv[0] else None
    if origen is not None and origen.suffix == ".pyz":
        return f"python {origen.name}"
    return "python -m andamio"


# --- Mensajes ---------------------------------------------------------------


def escribir(texto: str = "") -> None:
    print(texto)


def titulo(texto: str) -> None:
    print(color(texto, "negrita"))


def exito(texto: str) -> None:
    print(color(texto, "verde", "negrita"))


def aviso(texto: str) -> None:
    print(color("Atención: ", "amarillo", "negrita") + texto)


def error(mensaje: str, sugerencia: str | None = None) -> None:
    print(color("Error: ", "rojo", "negrita") + mensaje, file=sys.stderr)
    if sugerencia:
        print(color("Cómo seguir: ", "cian", "negrita") + sugerencia, file=sys.stderr)


def comando(texto: str) -> str:
    """Resalta un comando que el alumno tiene que escribir."""
    return color(texto, "cian", "negrita")


# --- Preguntas --------------------------------------------------------------


def leer(texto: str) -> str:
    try:
        return input(texto)
    except EOFError:
        raise Cancelado() from None


def preguntar(
    texto: str,
    validar: Callable[[str], T] | None = None,
    ejemplo: str | None = None,
    permitir_vacio: bool = False,
) -> T | str:
    """Pide un dato hasta que sea válido. `validar` lanza AndamioError si el dato no sirve."""
    sufijo = f" (ej: {ejemplo})" if ejemplo else ""
    while True:
        respuesta = leer(f"{texto}{sufijo}: ").strip()
        if not respuesta and not permitir_vacio:
            print(color("  Este dato es obligatorio.", "amarillo"))
            continue
        if validar is None or (not respuesta and permitir_vacio):
            return respuesta
        try:
            return validar(respuesta)
        except AndamioError as e:
            print(color(f"  {e.mensaje}", "amarillo"))
            if e.sugerencia:
                print(color(f"  {e.sugerencia}", "amarillo"))


def elegir(texto: str, opciones: Sequence[tuple[T, str]]) -> T:
    """Muestra opciones numeradas y devuelve la clave de la elegida."""
    print(texto)
    for i, (_, etiqueta) in enumerate(opciones, start=1):
        print(f"  {color(str(i), 'cian', 'negrita')}. {etiqueta}")
    while True:
        respuesta = leer("Elegí un número: ").strip()
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1][0]
        for clave, _ in opciones:
            if isinstance(clave, str) and clave.lower() == respuesta.lower():
                return clave
        print(color(f"  Escribí un número del 1 al {len(opciones)}.", "amarillo"))


_SI = {"s", "si", "sí", "y", "yes"}
_NO = {"n", "no"}


def confirmar(texto: str, defecto: bool | None = None) -> bool:
    while True:
        respuesta = leer(f"{texto} (s/n): ").strip().lower()
        if not respuesta and defecto is not None:
            return defecto
        if respuesta in _SI:
            return True
        if respuesta in _NO:
            return False
        print(color('  Respondé "s" (sí) o "n" (no).', "amarillo"))
