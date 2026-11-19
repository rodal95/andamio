"""La página web: demostraciones generadas con la versión actual y archivos completos."""

import re
import sys
import tempfile
from pathlib import Path

import pytest

import andamio
from andamio import stacks

RAIZ = Path(__file__).resolve().parents[2]
SITIO = RAIZ / "sitio"
sys.path.insert(0, str(RAIZ / "scripts"))
import sitio  # noqa: E402


@pytest.fixture(scope="module")
def datos():
    return sitio.generar()


def test_una_guia_por_tecnologia_y_variante(datos):
    assert datos["version"] == andamio.__version__
    assert [t["clave"] for t in datos["tecnologias"]] == [s.clave for s in stacks.ORDEN_MENU]
    for tecnologia, stack in zip(datos["tecnologias"], stacks.ORDEN_MENU):
        assert [v["clave"] for v in tecnologia["variantes"]] == (list(stack.variantes) or [""])
        for variante in tecnologia["variantes"]:
            assert [p["clave"] for p in variante["piezas"]] == list(stack.piezas)
            for pieza in variante["piezas"]:
                assert pieza["creados"], pieza["clave"]
                assert "Listo." in pieza["salida"] and "Error" not in pieza["salida"]


def test_cada_archivo_generado_tiene_su_explicacion(datos):
    """Si falla: agregá el archivo a DESCRIPCIONES (o CARPETAS) en scripts/sitio.py."""
    for tecnologia in datos["tecnologias"]:
        for variante in tecnologia["variantes"]:
            for archivo in variante["archivos"] + variante["archivos_crear"]:
                assert archivo["descripcion"], f"{tecnologia['clave']}/{variante['clave']}: {archivo['ruta']}"
            for pieza in variante["piezas"]:
                for modificado in pieza["modificados"]:
                    assert modificado["que"], (pieza["clave"], modificado["ruta"])


def test_sin_rutas_temporales(datos):
    texto = str(datos)
    temporal = Path(tempfile.gettempdir()).resolve()
    assert str(temporal) not in texto and tempfile.gettempdir() not in texto
    assert "SECRET_KEY=(se genera al azar" in texto


def test_sesion_del_menu(datos):
    eventos = datos["menu"]
    assert any(e["tipo"] == "entrada" for e in eventos)
    salida = "".join(e["texto"] for e in eventos if e["tipo"] == "salida")
    assert "Proyecto Django REST detectado." in salida
    assert "C:\\Users\\alumno\\mi-api" in salida


def test_la_app_de_consola_generada_funciona(datos):
    salida = datos["tecnologias"][0]["ejecucion"]["salida"]
    assert "Yerba Mate" in salida and "Tiene que ser un número entero" in salida


def test_existen_las_paginas_y_las_capturas():
    for stack in stacks.REGISTRO:
        pagina = SITIO / f"{stack.clave}.html"
        assert pagina.is_file(), pagina
        assert f'data-tecnologia="{stack.clave}"' in pagina.read_text(encoding="utf-8")
    codigo = (SITIO / "tecnologia.js").read_text(encoding="utf-8")
    for imagen in re.findall(r"img/[\w.-]+\.jpg", codigo):
        assert (SITIO / imagen).is_file(), f"falta {imagen}: ejecutá python scripts/capturas_sitio.py"
    for archivo in re.findall(r'\["([\w.-]+)", "[^"]+"\]', codigo):
        assert (SITIO / "ejemplos" / archivo).is_file(), archivo
