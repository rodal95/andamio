"""La documentación tiene que estar al día con el código."""

import re
from pathlib import Path

import andamio
from andamio import stacks
from andamio.stacks import django, python

RAIZ = Path(__file__).resolve().parents[2]
README = (RAIZ / "README.md").read_text(encoding="utf-8")


def test_la_instalacion_apunta_a_la_version_actual():
    """Si falla: actualizá la dirección del .whl en README.md al publicar una versión."""
    v = andamio.__version__
    assert f"releases/download/v{v}/andamio-{v}-py3-none-any.whl" in README


def test_la_primera_pantalla_es_corta():
    arriba = README.split("\n---\n")[0]
    assert len(arriba.splitlines()) <= 30
    assert "py -m pip install" in arriba  # Windows primero
    assert arriba.count("andamio ") >= 3


def test_el_readme_lista_todos_los_stacks_y_piezas():
    for stack in stacks.REGISTRO:
        fila = next((l for l in README.splitlines() if f"| `{stack.clave}` |" in l), None)
        assert fila, f"falta {stack.clave} en la tabla del README"
        for pieza in stack.piezas:
            assert f"`{pieza}`" in fila, f"falta la pieza {pieza} de {stack.clave}"


def test_el_readme_lista_todos_los_tipos_de_campo():
    filas = {re.match(r"\| `(\w+)` \|", l).group(1): l for l in README.splitlines() if re.match(r"\| `\w+` \|", l)}
    for tipo in django.TIPOS:
        assert tipo in filas, f"falta el tipo {tipo}"
    for tipo in python.TIPOS:
        assert "—" not in filas[tipo].split("|")[2], f"{tipo} existe en el stack python"


def test_changelog_tiene_la_version_actual():
    changelog = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{andamio.__version__}]" in changelog


def test_guia_docente():
    guia = (RAIZ / "docs" / "docente.md").read_text(encoding="utf-8")
    for tema in ("## Agregar una pieza", "## Agregar un stack", "## Publicar una versión", "## Tests"):
        assert tema in guia
