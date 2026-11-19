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
    assert "python -m pip install" in arriba  # Windows primero
    assert "python -m andamio" in arriba
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


def test_las_guias_tienen_todos_los_stacks_y_piezas():
    """Si falla: agregá el stack o la pieza a docs/guias/comandos.md."""
    comandos = (RAIZ / "docs" / "guias" / "comandos.md").read_text(encoding="utf-8")
    secciones = {s.split("\n")[0]: s for s in comandos.split("\n## ")[1:]}
    for stack in stacks.REGISTRO:
        seccion = next((s for titulo, s in secciones.items() if titulo.endswith(f"`{stack.clave}`")), None)
        assert seccion, f"falta la sección de {stack.clave} en docs/guias/comandos.md"
        for pieza in stack.piezas:
            assert f"| `{pieza}`" in seccion or (stack.extiende and f"| `{pieza}`" in secciones_de(secciones, stack.extiende)), (stack.clave, pieza)


def secciones_de(secciones, clave):
    return next((s for titulo, s in secciones.items() if titulo.endswith(f"`{clave}`")), "")


def test_los_enlaces_de_las_guias_existen():
    guias = RAIZ / "docs" / "guias"
    for archivo in [RAIZ / "README.md", *guias.glob("*.md")]:
        for destino in re.findall(r"\]\(([^)#:]+\.md)", archivo.read_text(encoding="utf-8")):
            assert (archivo.parent / destino).is_file(), f"{archivo.name} enlaza a {destino}, que no existe"
