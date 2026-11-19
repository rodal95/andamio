"""Motor de plantillas mínimo: reemplaza marcadores @@nombre@@.

Reglas:
- Un marcador se reemplaza por su valor tal cual.
- Si un marcador ocupa una línea él solo, cada línea del valor recibe la sangría
  de esa línea. Si el valor está vacío, la línea se elimina.
- Si queda un marcador que no existe, es un error (casi siempre es un error de tipeo
  en una plantilla editada).

Se recorre el texto una sola vez: el valor insertado nunca se vuelve a procesar,
así el resultado no depende del orden de los marcadores.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from andamio.nucleo.errores import AndamioError

MARCADOR = re.compile(r"@@([A-Za-z][A-Za-z0-9_]*)@@")
_SOLO_EN_LINEA = re.compile(r"^([ \t]*)@@([A-Za-z][A-Za-z0-9_]*)@@[ \t]*$")


def _error_desconocidos(desconocidos: set[str], contexto: dict[str, str], origen: str) -> AndamioError:
    lista = ", ".join(f"@@{m}@@" for m in sorted(desconocidos))
    donde = f"La plantilla '{origen}'" if origen else "La plantilla"
    disponibles = ", ".join(f"@@{m}@@" for m in sorted(contexto))
    return AndamioError(
        f"{donde} usa {lista}, que no existe.",
        f"Revisá si está bien escrito. Marcadores disponibles: {disponibles}",
    )


def renderizar(texto: str, contexto: dict[str, str], origen: str = "") -> str:
    desconocidos: set[str] = set()

    def reemplazar(m: re.Match[str]) -> str:
        clave = m.group(1)
        if clave in contexto:
            return contexto[clave]
        desconocidos.add(clave)
        return m.group(0)

    salida: list[str] = []
    for linea in texto.splitlines(keepends=True):
        cuerpo = linea.rstrip("\r\n")
        fin = linea[len(cuerpo):]
        solo = _SOLO_EN_LINEA.match(cuerpo)
        if solo and solo.group(2) in contexto:
            sangria, valor = solo.group(1), contexto[solo.group(2)]
            if valor == "":
                continue
            salto = "\r\n" if fin == "\r\n" else "\n"
            lineas = valor.replace("\r\n", "\n").split("\n")
            salida.append(salto.join(sangria + l if l.strip() else "" for l in lineas) + fin)
            continue
        salida.append(MARCADOR.sub(reemplazar, cuerpo) + fin)

    if desconocidos:
        raise _error_desconocidos(desconocidos, contexto, origen)
    return "".join(salida)


def renderizar_ruta(partes: tuple[str, ...], contexto: dict[str, str], origen: str = "") -> PurePosixPath:
    """Renderiza una ruta relativa. Un valor con "/" genera subcarpetas; las partes vacías se omiten."""
    resultado: list[str] = []
    for parte in partes:
        for sub in renderizar(parte, contexto, origen).split("/"):
            if sub in ("", "."):
                continue
            if sub == ".." or "\\" in sub or ":" in sub:
                raise AndamioError(f"La plantilla '{origen}' genera una ruta inválida: '{sub}'.")
            resultado.append(sub)
    if not resultado:
        raise AndamioError(f"La plantilla '{origen}' genera una ruta vacía.")
    return PurePosixPath(*resultado)


def marcadores_usados(texto: str) -> set[str]:
    return set(MARCADOR.findall(texto))
