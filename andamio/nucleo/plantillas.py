"""Ubicación y lectura de plantillas.

Las plantillas incorporadas viven en el paquete (`andamio/plantillas/<stack>/<pieza>/`) y
se leen con importlib.resources, así funcionan instaladas, con `python -m andamio` y
dentro de `andamio.pyz`. Si el proyecto del alumno tiene
`.andamio/plantillas/<stack>/<pieza>/`, se usa esa versión.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

CARPETA_PROYECTO = "_proyecto"
CARPETA_USUARIO = Path(".andamio") / "plantillas"
LEEME = "LEEME.md"

_IGNORADOS = {"__pycache__", ".DS_Store", "Thumbs.db", "desktop.ini"}
_EXT_BINARIAS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".ttf", ".otf", ".woff", ".woff2"}

# Algunos archivos no se pueden guardar con su nombre real dentro del paquete
# (un .gitignore anidado afectaría al repo de andamio). Se guardan sin el punto.
_RENOMBRAR = {"gitignore": ".gitignore"}


@dataclass(frozen=True)
class ArchivoPlantilla:
    partes: tuple[str, ...]  # ruta relativa dentro de la carpeta de la plantilla
    contenido: bytes

    @property
    def ruta(self) -> str:
        return "/".join(self.partes)

    @property
    def texto(self) -> str | None:
        """Contenido como texto, o None si es un archivo binario (se copia sin procesar)."""
        if Path(self.partes[-1]).suffix.lower() in _EXT_BINARIAS:
            return None
        try:
            # utf-8-sig descarta el BOM que agregan algunos editores de Windows.
            return self.contenido.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None


def carpeta_incorporada(stack: str) -> Traversable:
    return resources.files("andamio") / "plantillas" / stack


def carpeta_personalizada(raiz: Path, stack: str, pieza: str) -> Path:
    return raiz / CARPETA_USUARIO / stack / pieza


def leer_arbol(carpeta: Traversable, ignorar_leeme: bool = True) -> list[ArchivoPlantilla]:
    archivos: list[ArchivoPlantilla] = []

    def recorrer(actual: Traversable, partes: tuple[str, ...]) -> None:
        for hijo in sorted(actual.iterdir(), key=lambda h: h.name):
            if hijo.name in _IGNORADOS or hijo.name.endswith(".pyc"):
                continue
            if hijo.is_dir():
                recorrer(hijo, partes + (hijo.name,))
            elif not (ignorar_leeme and not partes and hijo.name == LEEME):
                nombre = _RENOMBRAR.get(hijo.name, hijo.name)
                archivos.append(ArchivoPlantilla(partes + (nombre,), hijo.read_bytes()))

    recorrer(carpeta, ())
    return archivos
