"""El Python que genera andamio no usa nombres sin definir ni define dos veces el mismo.

Compilar no alcanza: un nombre sin definir (por ejemplo, una variable que se renombró en
la plantilla y no en el código que arma un marcador) compila igual y falla recién al
ejecutar. Este control corre sin instalar Django, FastAPI ni Reflex.
"""

import ast

import pytest

from andamio import stacks
from andamio.cli import main

from .barrido import _redefiniciones, nombres_sin_definir

STACKS_PYTHON = ["python", "django", "django-web", "fastapi", "reflex"]
TODOS_LOS_TIPOS = ["texto:str", "detalle:text", "cantidad:int", "precio:decimal", "peso:float", "activo:bool",
                   "alta:date", "turno:datetime", "correo:email"]


def _piezas(stack):
    for clave, pieza in stack.piezas.items():
        nombre, *campos = pieza.ejemplo.split() or [pieza.nombre_defecto]
        if clave not in ("tema", "ui", "login"):
            nombre = f"{nombre} {clave.replace('-', ' ')}"  # cada pieza con su nombre (crud y crud-api no chocan)
        if pieza.usa_campos:
            campos = TODOS_LOS_TIPOS if stack.clave != "python" else ["texto:str", "cantidad:int", "peso:float"]
        yield [clave, nombre, *campos]
        if "protegido" in pieza.opciones:
            yield [clave, f"{nombre}-protegido", *campos, "--protegido"]


@pytest.mark.parametrize("clave", STACKS_PYTHON)
@pytest.mark.parametrize("guia", [True, False], ids=["con-guia", "sin-guia"])
def test_python_generado_sin_nombres_sin_definir(clave, guia, en_carpeta, monkeypatch):
    stack = stacks.por_clave(clave)
    extra = [] if guia else ["--sin-guia"]
    assert main(["crear", clave, "proy", *extra]) == 0
    raiz = en_carpeta / "proy"
    monkeypatch.chdir(raiz)
    for argumentos in _piezas(stack):
        if argumentos[0] == "login":
            argumentos = ["login"]
        assert main(["nuevo", *argumentos, *extra]) == 0, argumentos
    problemas = []
    for archivo in sorted(raiz.rglob("*.py")):
        texto = archivo.read_text(encoding="utf-8")
        arbol = ast.parse(texto, filename=str(archivo))
        rel = archivo.relative_to(raiz).as_posix()
        problemas += [f"{rel}: {p}" for p in nombres_sin_definir(arbol) + _redefiniciones(arbol, texto.splitlines())]
    assert not problemas, "\n".join(problemas)
