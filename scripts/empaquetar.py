"""Arma los archivos que se publican en cada Release (además del .whl).

    python scripts/empaquetar.py [carpeta_destino]

- andamio.pyz           un solo archivo: `python andamio.pyz` desde cualquier carpeta.
- andamio-X.Y.Z.zip     el código: se descomprime y se usa con `python -m andamio`
                        (o se instala con `pip install .`).

Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
import zipapp
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def version() -> str:
    texto = (RAIZ / "andamio" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__ = "([^"]+)"', texto).group(1)


def armar_pyz(destino: Path) -> Path:
    archivo = destino / "andamio.pyz"
    with tempfile.TemporaryDirectory() as temporal:
        fuente = Path(temporal) / "fuente"
        shutil.copytree(RAIZ / "andamio", fuente / "andamio", ignore=IGNORAR)
        zipapp.create_archive(
            fuente,
            archivo,
            interpreter="/usr/bin/env python3",
            main="andamio.cli:main",
            compressed=True,
        )
    return archivo


def armar_zip(destino: Path) -> Path:
    nombre = f"andamio-{version()}"
    archivo = destino / f"{nombre}.zip"
    with tempfile.TemporaryDirectory() as temporal:
        carpeta = Path(temporal) / nombre
        shutil.copytree(RAIZ / "andamio", carpeta / "andamio", ignore=IGNORAR)
        for suelto in ("README.md", "CHANGELOG.md", "pyproject.toml"):
            shutil.copy2(RAIZ / suelto, carpeta / suelto)
        with zipfile.ZipFile(archivo, "w", zipfile.ZIP_DEFLATED) as zip_:
            for ruta in sorted(carpeta.rglob("*")):
                if ruta.is_file():
                    zip_.write(ruta, ruta.relative_to(temporal).as_posix())
    return archivo


def notas_de_version(numero: str) -> str:
    """El texto de la versión en CHANGELOG.md, para la descripción de la Release."""
    changelog = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    seccion = re.search(rf"^## \[{re.escape(numero)}\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.S | re.M)
    if not seccion:
        raise SystemExit(f"No encontré la sección [{numero}] en CHANGELOG.md")
    # Sin las referencias de enlaces del final del archivo ([1.0.0]: https://...).
    texto = re.sub(r"^\[[^\]]+\]: \S+\n?", "", seccion.group(1), flags=re.M)
    return texto.strip() + "\n"


def main(argumentos: list[str]) -> None:
    if argumentos[:1] == ["notas"]:
        sys.stdout.write(notas_de_version(argumentos[1] if len(argumentos) > 1 else version()))
        return
    destino = Path(argumentos[0] if argumentos else RAIZ / "dist").resolve()
    destino.mkdir(parents=True, exist_ok=True)
    for archivo in (armar_pyz(destino), armar_zip(destino)):
        print(f"{archivo}  ({archivo.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
