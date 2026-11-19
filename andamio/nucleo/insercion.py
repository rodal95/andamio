"""Inserción de líneas en archivos existentes.

Los archivos generados tienen líneas marcador como:

    # --- andamio:apps (no borrar esta línea) ---

Las líneas nuevas se insertan justo antes del marcador, con su misma sangría.
El marcador se busca por la clave (`andamio:apps`), así que cambiar el resto del
comentario no lo rompe.
"""

from __future__ import annotations

import re


def linea_marcador(clave: str, comentario: str = "#") -> str:
    if comentario == "{/*":  # comentario dentro de JSX
        return f"{{/* --- andamio:{clave} (no borrar esta línea) --- */}}"
    return f"{comentario} --- andamio:{clave} (no borrar esta línea) ---"


def estilo_salto(texto: str) -> str:
    """Respeta el fin de línea del archivo (\\r\\n si fue editado en Windows con esa opción)."""
    return "\r\n" if "\r\n" in texto else "\n"


def ya_presente(texto: str, bloque: str) -> bool:
    """True si todas las líneas del bloque ya están en el archivo (evita duplicar)."""
    existentes = {l.strip() for l in texto.splitlines()}
    lineas = [l.strip() for l in bloque.split("\n") if l.strip()]
    return bool(lineas) and all(l in existentes for l in lineas)


def insertar_antes_de_marcador(texto: str, clave: str, bloque: str) -> str | None:
    """Inserta el bloque antes de la línea del marcador. Devuelve None si no hay marcador."""
    buscado = f"andamio:{clave}"
    lineas = texto.splitlines(keepends=True)
    for i, linea in enumerate(lineas):
        if re.search(rf"{re.escape(buscado)}\b", linea):
            sangria = re.match(r"[ \t]*", linea).group(0)
            salto = estilo_salto(texto)
            nuevas = [(sangria + l if l.strip() else "") + salto for l in bloque.split("\n")]
            return "".join(lineas[:i] + nuevas + lineas[i:])
    return None


def agregar_al_final(texto: str, bloque: str) -> str:
    salto = estilo_salto(texto) if texto else "\n"
    if texto and not texto.endswith("\n"):
        texto += salto
    return texto + salto.join(bloque.split("\n")) + salto
