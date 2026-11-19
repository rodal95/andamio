"""`andamio plantillas exportar`: se implementa en la fase 4."""

from __future__ import annotations

from pathlib import Path

from andamio.nucleo.errores import AndamioError


def exportar(cwd: Path, pieza: str | None = None) -> int:
    raise AndamioError("La exportación de plantillas todavía no está disponible en esta versión.")
