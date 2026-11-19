"""Los archivos de la Release funcionan: andamio.pyz y el .zip con python -m andamio."""

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import andamio

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))
import empaquetar  # noqa: E402


def ejecutar(argumentos, cwd):
    resultado = subprocess.run(
        [sys.executable, *argumentos],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    return resultado.stdout


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    destino = tmp_path_factory.mktemp("dist")
    empaquetar.main([str(destino)])
    return destino


def test_pyz_funciona_desde_cualquier_carpeta(dist, tmp_path):
    pyz = dist / "andamio.pyz"
    assert andamio.__version__ in ejecutar([str(pyz), "--version"], tmp_path)
    ejecutar([str(pyz), "crear", "react-native", "app"], tmp_path)
    # El ícono binario sale intacto desde adentro del .pyz.
    original = (RAIZ / "andamio/plantillas/react-native/_proyecto/assets/icon.png").read_bytes()
    assert (tmp_path / "app/assets/icon.png").read_bytes() == original
    ejecutar([str(pyz), "nuevo", "pantalla", "detalle", "--carpeta", "(tabs)"], tmp_path / "app")
    assert (tmp_path / "app/app/(tabs)/detalle.tsx").is_file()


def test_pyz_no_incluye_archivos_compilados(dist):
    nombres = zipfile.ZipFile(dist / "andamio.pyz").namelist()
    assert "__main__.py" in nombres
    assert not [n for n in nombres if "__pycache__" in n or n.endswith(".pyc")]


def test_zip_con_python_m_andamio(dist, tmp_path):
    archivo = dist / f"andamio-{andamio.__version__}.zip"
    with zipfile.ZipFile(archivo) as zip_:
        zip_.extractall(tmp_path)
    carpeta = tmp_path / f"andamio-{andamio.__version__}"
    for suelto in ("README.md", "CHANGELOG.md", "pyproject.toml", "andamio/__main__.py"):
        assert (carpeta / suelto).is_file(), suelto
    assert andamio.__version__ in ejecutar(["-m", "andamio", "--version"], carpeta)


def test_notas_de_version_del_changelog():
    notas = empaquetar.notas_de_version(andamio.__version__)
    assert "Stack `django`" in notas
    assert "## [" not in notas
    assert "]: https://" not in notas
