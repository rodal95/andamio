"""Controles sobre las plantillas incorporadas de todos los stacks y variantes."""

import pytest

from andamio import stacks
from andamio.nucleo import plantillas
from andamio.nucleo.generador import carpeta_pieza, carpeta_plantillas
from andamio.nucleo.motor import marcadores_usados
from andamio.nucleo.nombres import MARCADORES_NOMBRE


def _variantes(stack):
    return list(stack.variantes) or [""]


def _combinaciones():
    for stack in stacks.REGISTRO:
        for variante in _variantes(stack):
            yield pytest.param(stack, variante, id=f"{stack.clave}-{variante or 'unica'}")


def _piezas():
    for stack in stacks.REGISTRO:
        for variante in _variantes(stack):
            for pieza in stack.piezas.values():
                yield pytest.param(stack, variante, pieza, id=f"{stack.clave}-{variante or 'unica'}-{pieza.clave}")


@pytest.mark.parametrize("stack, variante, pieza", list(_piezas()))
def test_cada_marcador_de_una_pieza_esta_declarado(stack, variante, pieza):
    """Si falla: agregá el marcador a `marcadores` de la Pieza (así aparece en el LEEME)."""
    declarados = set(MARCADORES_NOMBRE) | set(pieza.marcadores)
    carpeta = carpeta_pieza(stack, pieza, variante)  # la propia o la del stack que extiende
    assert carpeta.is_dir(), f"falta la carpeta {stack.clave}/{variante}/{pieza.clave}"
    usados = set()
    for archivo in plantillas.leer_arbol(carpeta):
        usados |= marcadores_usados(archivo.ruta)
        if archivo.texto is not None:
            usados |= marcadores_usados(archivo.texto)
    for insercion in pieza.inserciones:
        usados |= marcadores_usados(insercion.archivo + insercion.texto + insercion.descripcion)
    for ruta in pieza.existe_si:
        usados |= marcadores_usados(ruta)
    assert usados - declarados == set()


@pytest.mark.parametrize("stack, variante", list(_combinaciones()))
def test_cada_variante_tiene_plantilla_de_proyecto(stack, variante):
    carpeta = carpeta_plantillas(stack, variante) / plantillas.CARPETA_PROYECTO
    assert carpeta.is_dir()
    assert plantillas.leer_arbol(carpeta, ignorar_leeme=False)


@pytest.mark.parametrize("stack", [s for s in stacks.REGISTRO if s.variantes], ids=lambda s: s.clave)
def test_las_variantes_tienen_las_mismas_piezas_y_marcadores(stack):
    for variante in stack.variantes:
        assert set(stack.marcadores_variante[variante]) == set(stack.marcadores_variante[next(iter(stack.variantes))])


@pytest.mark.parametrize("variante, archivo", [("ts", "@@nombreCamel@@Service.ts"), ("js", "@@nombreCamel@@Service.js")])
def test_el_servicio_es_igual_en_react_y_react_native(variante, archivo):
    """Coherencia: el mismo servicio en los dos stacks (solo cambia http)."""
    react = plantillas.carpeta_incorporada("react") / variante / "servicio" / "src" / "services" / archivo
    nativo = plantillas.carpeta_incorporada("react-native") / variante / "servicio" / "services" / archivo
    assert react.read_text(encoding="utf-8") == nativo.read_text(encoding="utf-8")


@pytest.mark.parametrize("variante, extension", [("ts", "ts"), ("js", "js")])
def test_el_crud_trae_el_mismo_servicio_que_la_pieza_servicio(variante, extension):
    base = plantillas.carpeta_incorporada("react") / variante
    for archivo in ("http", "@@nombreCamel@@Service"):
        servicio = base / "servicio" / "src" / "services" / f"{archivo}.{extension}"
        crud = base / "crud" / "src" / "services" / f"{archivo}.{extension}"
        assert crud.read_text(encoding="utf-8") == servicio.read_text(encoding="utf-8"), archivo


@pytest.mark.parametrize("variante", ["ts", "js"])
def test_la_version_del_router_coincide(variante):
    import json

    from andamio.stacks._js import VERSION_ROUTER

    paquete = json.loads((plantillas.carpeta_incorporada("react") / variante / "_proyecto" / "package.json").read_text(encoding="utf-8"))
    assert paquete["dependencies"]["react-router"] == VERSION_ROUTER


@pytest.mark.parametrize("stack", [s for s in stacks.REGISTRO if s.variantes], ids=lambda s: s.clave)
def test_las_plantillas_js_no_tienen_sintaxis_de_typescript(stack):
    import re

    tipos = re.compile(r"^import type |\binterface \w+ \{|: (string|number|boolean)\b[;,)]|<T>\(")
    raiz = carpeta_plantillas(stack, "js")
    for carpeta in raiz.iterdir():
        for archivo in plantillas.leer_arbol(carpeta, ignorar_leeme=False):
            if archivo.texto is None or not archivo.ruta.endswith((".js", ".jsx")):
                continue
            for numero, linea in enumerate(archivo.texto.splitlines(), 1):
                # En los comentarios JSDoc los tipos sí van (los lee el editor): {(id: number) => ...}
                if linea.lstrip().startswith(("*", "/**", "//")):
                    continue
                assert not tipos.search(linea), f"{carpeta.name}/{archivo.ruta}:{numero}: {linea}"


def test_carpeta_combinada(tmp_path):
    """Un stack que extiende a otro reemplaza solo los archivos que cambian de una pieza."""
    base, propia = tmp_path / "base", tmp_path / "propia"
    for ruta, texto in {"a.txt": "base", "sub/b.txt": "base", "sub/c.txt": "base"}.items():
        (base / ruta).parent.mkdir(parents=True, exist_ok=True)
        (base / ruta).write_text(texto)
    for ruta, texto in {"sub/b.txt": "propia", "nuevo.txt": "propia"}.items():
        (propia / ruta).parent.mkdir(parents=True, exist_ok=True)
        (propia / ruta).write_text(texto)
    archivos = {a.ruta: a.contenido.decode() for a in plantillas.leer_arbol(plantillas.CarpetaCombinada(propia, base))}
    assert archivos == {"a.txt": "base", "sub/b.txt": "propia", "sub/c.txt": "base", "nuevo.txt": "propia"}
    assert plantillas.CarpetaCombinada(tmp_path / "no", base).is_dir()
