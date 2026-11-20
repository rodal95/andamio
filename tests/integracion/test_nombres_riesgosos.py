"""Nombres que generaban código roto (los encontró el barrido de test_barrido.py).

Cada uno ahora se rechaza con un mensaje que explica por qué y qué hacer.
"""

import pytest

from andamio.cli import main


def _proyecto(en_carpeta, monkeypatch, stack, *extra):
    assert main(["crear", stack, "proy", *extra]) == 0
    monkeypatch.chdir(en_carpeta / "proy")
    return en_carpeta / "proy"


@pytest.mark.parametrize(
    "stack, extra, argumentos, esperado",
    [
        # El router de FastAPI ya tiene una variable `consulta` (la consulta a la base).
        ("fastapi", [], ["recurso", "consulta", "detalle:str"], "consulta"),
        # Variables del router de Express y de las rutas de Next.js.
        ("express", ["--js"], ["recurso", "filtro", "nombre:str"], "filtros"),
        ("express", ["--js"], ["recurso", "texto", "nombre:str"], "texto"),
        ("next-fullstack", ["--js"], ["recurso", "parametro", "nombre:str"], "parametros"),
        # Variables del <script setup> del crud de Vue.
        ("vue", [], ["crud", "error", "mensaje:str"], "error"),
        # Reflex: la página "app" choca con app = rx.App(); "plantilla" con la función plantilla().
        ("reflex", [], ["pagina", "app"], "app"),
        ("reflex", [], ["pagina", "plantilla"], "plantilla"),
        # None, True y False son palabras reservadas de Python (en PascalCase).
        ("django", [], ["recurso", "none", "dato:str"], "None"),
        # Windows no deja crear archivos con estos nombres.
        ("react", [], ["componente", "Aux"], "Windows"),
    ],
)
def test_nombres_rechazados(en_carpeta, monkeypatch, capsys, stack, extra, argumentos, esperado):
    raiz = _proyecto(en_carpeta, monkeypatch, stack, *extra)
    antes = sorted(raiz.rglob("*"))
    capsys.readouterr()
    assert main(["nuevo", *argumentos]) == 1
    error = capsys.readouterr().err
    assert esperado in error, error
    assert sorted(raiz.rglob("*")) == antes  # no se escribió nada


@pytest.mark.parametrize("nombre", ["email", "random", "calendar"])
def test_reflex_no_acepta_un_proyecto_con_nombre_de_modulo_de_python(en_carpeta, capsys, nombre):
    assert main(["crear", "reflex", nombre]) == 1
    assert "módulo de Python" in capsys.readouterr().err
    assert not (en_carpeta / nombre).exists()


def test_proyecto_con_nombre_reservado_de_windows(en_carpeta, capsys):
    assert main(["crear", "react", "con"]) == 1
    assert "Windows" in capsys.readouterr().err


@pytest.mark.parametrize("campo", ["estado", "filas"])
def test_web_crud_no_acepta_campos_que_son_ids_de_la_pagina(en_carpeta, monkeypatch, capsys, campo):
    _proyecto(en_carpeta, monkeypatch, "web")
    assert main(["nuevo", "crud", "pedido", "cliente:str", f"{campo}:str"]) == 1
    assert f"campo '{campo}'" in capsys.readouterr().err


def test_django_web_crud_no_pisa_la_ruta_de_una_pagina(en_carpeta, monkeypatch, capsys):
    raiz = _proyecto(en_carpeta, monkeypatch, "django-web")
    assert main(["nuevo", "pagina", "Productos"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre:str"]) == 1
    assert "/productos/" in capsys.readouterr().err
    assert (raiz / "config/urls.py").read_text(encoding="utf-8").count('path("productos/"') == 1
    # Con otro plural, la ruta es otra y se puede.
    assert main(["nuevo", "crud", "producto", "nombre:str", "--plural", "articulos"]) == 0


def test_next_fullstack_la_pista_del_crud_lleva_el_plural(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch, "next-fullstack")
    capsys.readouterr()
    assert main(["nuevo", "crud", "lapiz", "nombre:str", "--plural", "lapices_color"]) == 0
    salida = capsys.readouterr().out
    assert "nuevo recurso lapiz nombre:str --plural lapices_color" in salida


@pytest.mark.parametrize(
    "stack, extra, argumentos",
    [
        # Nombres comunes que antes chocaban con variables internas de las plantillas.
        ("fastapi", [], ["recurso", "sesion", "duracion:int"]),
        ("express", ["--js"], ["recurso", "orden", "total:decimal"]),
        ("express", ["--js"], ["recurso", "respuesta", "texto_respuesta:str"]),
        ("next-fullstack", ["--js"], ["recurso", "orden", "total:decimal"]),
        ("reflex", [], ["crud", "sesion", "duracion:int"]),
        ("reflex", [], ["crud", "registro", "detalle:str"]),
        ("django-web", [], ["crud", "respuesta", "texto_respuesta:str"]),
    ],
)
def test_nombres_comunes_se_pueden_usar(en_carpeta, monkeypatch, stack, extra, argumentos):
    _proyecto(en_carpeta, monkeypatch, stack, *extra)
    assert main(["nuevo", *argumentos]) == 0
