"""Modo guiado (por defecto) y --sin-guia, marcas TODO(logica) y el comando pendientes."""

import py_compile

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo import plantillas
from andamio.nucleo.generador import archivos_proyecto, carpeta_pieza
from andamio.nucleo.motor import es_linea_de_guia, renderizar


def test_el_motor_quita_la_palabra_guia_o_la_linea():
    texto = "# guía: el modelo @@Nombre@@\nx = 1\n    // guía: hola\n{/* guía: jsx */}\n<!-- guia: html -->\n"
    assert renderizar(texto, {"Nombre": "Producto"}) == "# el modelo Producto\nx = 1\n    // hola\n{/* jsx */}\n<!-- html -->\n"
    assert renderizar(texto, {"Nombre": "Producto"}, guia=False) == "x = 1\n"


def test_guia_solo_cuenta_si_la_linea_es_un_comentario_entero():
    assert es_linea_de_guia("  # guía: algo")
    assert not es_linea_de_guia("x = 1  # guía: algo")  # comentario al final de una línea de código
    assert renderizar("x = 1  # guía: algo\n", {}, guia=False) == "x = 1  # guía: algo\n"


def _todas_las_plantillas():
    for stack in stacks.REGISTRO:
        for variante in list(stack.variantes) or [""]:
            archivos = list(archivos_proyecto(stack, variante))
            for pieza in stack.piezas.values():
                archivos += plantillas.leer_arbol(carpeta_pieza(stack, pieza, variante))
            for archivo in archivos:
                if archivo.texto is not None:
                    yield f"{stack.clave}/{variante}/{archivo.ruta}", archivo.texto


def test_cada_guia_de_las_plantillas_es_una_linea_de_comentario_entera():
    """Si falla: la guía tiene que ir sola en su línea, así --sin-guia la puede borrar entera."""
    for origen, texto in _todas_las_plantillas():
        for numero, linea in enumerate(texto.splitlines(), 1):
            if "guía:" in linea or "guia:" in linea:
                assert es_linea_de_guia(linea), f"{origen}:{numero}: {linea}"


CASOS = [
    pytest.param(s, v, clave, id=f"{s.clave}-{v or 'unica'}-{clave}")
    for s in stacks.REGISTRO
    for v in (list(s.variantes) or [""])
    for clave, pieza in s.piezas.items()
    if pieza.lectura
]


@pytest.mark.parametrize("stack, variante, clave", CASOS)
def test_sin_guia_no_quedan_guias_y_quedan_las_marcas(stack, variante, clave, en_carpeta, monkeypatch):
    pieza = stack.piezas[clave]
    assert main(["crear", stack.clave, "proy", "--sin-guia", *(["--variante", variante] if variante else [])]) == 0
    raiz = en_carpeta / "proy"
    monkeypatch.chdir(raiz)
    for previo in pieza.preparar:
        assert main(["nuevo", *previo.split(), "--sin-guia"]) == 0
    antes = {p: p.read_bytes() for p in raiz.rglob("*") if p.is_file()}
    nombre, *campos = pieza.ejemplo.split() or [pieza.nombre_defecto]
    assert main(["nuevo", clave, nombre, *campos, "--sin-guia"]) == 0
    cambiados = [p for p in raiz.rglob("*") if p.is_file() and antes.get(p) != p.read_bytes()]
    for ruta in cambiados:
        texto = ruta.read_text(encoding="utf-8")
        assert "guía:" not in texto and "guia:" not in texto, ruta
        if ruta.suffix == ".py":
            py_compile.compile(str(ruta), doraise=True)


def test_con_guia_el_codigo_explica_y_marca_la_logica(en_carpeta, monkeypatch):
    assert main(["crear", "django", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    assert main(["nuevo", "recurso", "producto", "nombre:str", "precio:decimal"]) == 0
    modelo = (en_carpeta / "api/productos/models.py").read_text(encoding="utf-8")
    assert modelo.startswith("# El modelo: la tabla productos")
    assert "TODO(logica)" in (en_carpeta / "api/productos/serializers.py").read_text(encoding="utf-8")


def test_sin_guia_quedan_las_marcas_de_logica(en_carpeta, monkeypatch):
    assert main(["crear", "django", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    assert main(["new", "resource", "producto", "nombre:str", "--no-guide"]) == 0
    modelo = (en_carpeta / "api/productos/models.py").read_text(encoding="utf-8")
    assert modelo.startswith("from django.db import models")
    assert "TODO(logica)" in (en_carpeta / "api/productos/serializers.py").read_text(encoding="utf-8")


def test_pendientes(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "fastapi", "api"]) == 0
    raiz = en_carpeta / "api"
    monkeypatch.chdir(raiz)
    capsys.readouterr()
    assert main(["pendientes"]) == 0
    assert "No hay marcas TODO(logica)" in capsys.readouterr().out
    assert main(["nuevo", "recurso", "producto", "nombre:str"]) == 0
    # Lo que está en dependencias, compilados o documentos no cuenta.
    (raiz / "node_modules").mkdir()
    (raiz / "node_modules/x.js").write_text("// TODO(logica): no\n", encoding="utf-8")
    (raiz / "NOTAS.md").write_text("TODO(logica): no\n", encoding="utf-8")
    monkeypatch.chdir(raiz / "app")  # funciona desde cualquier subcarpeta
    capsys.readouterr()
    assert main(["todo"]) == 0
    salida = capsys.readouterr().out
    assert "app/productos/modelo.py" in salida and "app/productos/router.py" in salida
    assert "reglas antes de guardar" in salida
    assert "node_modules" not in salida and "NOTAS.md" not in salida
    assert "2 marcas en 2 archivos" in salida
