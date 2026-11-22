"""`nuevo servicio ... --solo crear`: el servicio con algunas funciones, y el formulario que
solo envía (--datos x --form con un servicio sin obtener ni actualizar)."""

import json

import pytest

from andamio.cli import main
from andamio.nucleo.errores import AndamioError
from andamio.stacks import _js


def _proyecto(en_carpeta, monkeypatch, stack, *extra):
    assert main(["crear", stack, "web", *extra]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    return raiz


def _funciones(texto: str) -> list[str]:
    """Las funciones del objeto del servicio, en orden."""
    inicio = texto.index(" = {\n")
    cuerpo = texto[inicio : texto.index("\n};", inicio)]
    return [linea.split(":")[0].strip() for linea in cuerpo.splitlines() if linea.startswith("  ") and not linea.lstrip().startswith(("/", "*"))]


# --- normalizar_solo ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("crear", "crear"),
        ("Crear", "crear"),
        ("post", "crear"),
        ("create", "crear"),
        ("obtener,listar", "listar,obtener"),  # en el orden del servicio
        ("listar, obtener", "listar,obtener"),
        ("delete patch", "actualizar,eliminar"),
        ("crear,crear", "crear"),
    ],
)
def test_normalizar_solo(texto, esperado):
    assert _js.normalizar_solo(texto) == esperado


@pytest.mark.parametrize("texto", ["enviar", "get-all", "", " , "])
def test_normalizar_solo_rechaza_lo_que_no_es_una_funcion(texto):
    with pytest.raises(AndamioError):
        _js.normalizar_solo(texto)


# --- El servicio -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stack, extra, archivo",
    [
        ("react", [], "src/services/contactoService.ts"),
        ("react", ["--js"], "src/services/contactoService.js"),
        ("next", [], "services/contactoService.ts"),
        ("vue", [], "src/services/contactoService.js"),
        ("react-native", [], "services/contactoService.ts"),
        ("web", [], "js/servicios/contactoServicio.js"),
    ],
)
def test_servicio_solo_con_esas_funciones(en_carpeta, monkeypatch, stack, extra, archivo):
    raiz = _proyecto(en_carpeta, monkeypatch, stack, *extra)
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "email:email", "--solo", "crear,listar"]) == 0
    texto = (raiz / archivo).read_text(encoding="utf-8")
    assert _funciones(texto) == ["listar", "crear"]
    assert "obtener" not in texto.split(" = {")[-1]  # ni la función ni su comentario
    assert "// Solo listar, crear (--solo listar,crear)" in texto
    # El historial lo recuerda (andamio mapa lo muestra).
    linea = (raiz / ".andamio/historial.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    assert json.loads(linea)["opciones"] == {"solo": "listar,crear"}


def test_servicio_sin_solo_tiene_todas(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str"]) == 0
    texto = (raiz / "src/services/contactoService.ts").read_text(encoding="utf-8")
    assert _funciones(texto) == list(_js.OPERACIONES)
    assert "--solo" not in texto


def test_servicio_solo_sin_guia_no_lleva_el_comentario(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", "crear", "--sin-guia"]) == 0
    texto = (raiz / "src/services/contactoService.ts").read_text(encoding="utf-8")
    assert _funciones(texto) == ["crear"] and "--solo" not in texto


@pytest.mark.parametrize(
    "solo, consulta, formulario",
    [
        ("crear", False, False),
        ("listar", True, False),
        ("obtener,eliminar", True, False),
        ("obtener,crear,actualizar", True, True),
    ],
)
def test_servicio_solo_crea_los_hooks_que_puede_usar(en_carpeta, monkeypatch, solo, consulta, formulario):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", solo]) == 0
    assert (raiz / "src/hooks/useConsulta.ts").exists() == consulta
    assert (raiz / "src/hooks/useFormulario.ts").exists() == formulario


def test_solo_no_es_para_otras_piezas(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "pagina", "Inicio", "--solo", "crear"]) != 0
    assert "no acepta la opción --solo" in capsys.readouterr().err


def test_solo_en_ingles(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["new", "service", "contacto", "nombre:str", "--only", "post"]) == 0
    assert _funciones((raiz / "src/services/contactoService.ts").read_text(encoding="utf-8")) == ["crear"]


# --- Las páginas controlan que el servicio tenga lo que usan -----------------------------


@pytest.mark.parametrize(
    "opciones, falta",
    [
        ([], "listar"),
        (["--uno"], "obtener"),
    ],
)
def test_la_pagina_necesita_la_funcion_que_usa(en_carpeta, monkeypatch, capsys, opciones, falta):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", "crear"]) == 0
    assert main(["nuevo", "pagina", "Contactos", "--datos", "contacto", *opciones]) != 0
    assert f"contactoService.{falta}" in capsys.readouterr().err
    assert not (raiz / "src/pages/ContactosPage").exists()


def test_el_formulario_necesita_crear(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "producto", "nombre:str", "--solo", "listar,obtener"]) == 0
    assert main(["nuevo", "pagina", "Producto", "--datos", "producto", "--form"]) != 0
    assert "productoService.crear" in capsys.readouterr().err


# --- El formulario que solo envía --------------------------------------------------------


def test_formulario_que_solo_envia_react(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "email:email", "mensaje:text", "--solo", "crear"]) == 0
    assert main(["nuevo", "pagina", "Contacto", "--datos", "contacto", "--form"]) == 0
    pagina = (raiz / "src/pages/ContactoPage/ContactoPage.tsx").read_text(encoding="utf-8")
    assert "useFormulario" not in pagina and "useParams" not in pagina and "useNavigate" not in pagina
    assert "import { contactoService, type ContactoDatos } from '../../services/contactoService';" in pagina
    assert "await contactoService.crear(datos);" in pagina
    assert "e instanceof ErrorApi && e.estado === 400" in pagina
    assert "{enviando ? 'Enviando…' : 'Enviar'}" in pagina and "¡Listo! Se envió." in pagina
    assert "TODO(logica)" in pagina and "String(datos.nombre).trim().length < 3" in pagina
    assert ".exito" in (raiz / "src/pages/ContactoPage/ContactoPage.module.css").read_text(encoding="utf-8")
    app = (raiz / "src/App.tsx").read_text(encoding="utf-8")
    assert 'path="/contacto"' in app and "/contacto/:id" not in app  # no edita: sin ruta con id
    assert not (raiz / "src/hooks/useFormulario.ts").exists()
    assert not (raiz / "src/hooks/useConsulta.ts").exists()


def test_formulario_que_solo_envia_react_js(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react", "--js")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", "crear"]) == 0
    assert main(["nuevo", "pagina", "Contacto", "--datos", "contacto", "--form"]) == 0
    pagina = (raiz / "src/pages/ContactoPage/ContactoPage.jsx").read_text(encoding="utf-8")
    assert "/** @typedef {import('../../services/contactoService').ContactoDatos} ContactoDatos */" in pagina
    assert "useState(VACIO)" in pagina and " as " not in pagina


def test_formulario_que_solo_envia_con_relacion_usa_use_consulta(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "categoria", "nombre:str"]) == 0
    assert main(["nuevo", "servicio", "pedido", "detalle:str", "categoria:fk", "--solo", "crear"]) == 0
    assert main(["nuevo", "pagina", "Pedido", "--datos", "pedido", "--form"]) == 0
    pagina = (raiz / "src/pages/PedidoPage/PedidoPage.tsx").read_text(encoding="utf-8")
    assert "const { datos: categorias } = useConsulta(categoriaService.listar);" in pagina
    assert "useFormulario" not in pagina


def test_un_servicio_completo_sigue_editando(en_carpeta, monkeypatch):
    """Sin --solo, --form es el de siempre: useFormulario y la ruta para editar."""
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    assert main(["nuevo", "pagina", "ProductoEditar", "--datos", "producto", "--form"]) == 0
    assert "useFormulario(" in (raiz / "src/pages/ProductoEditarPage/ProductoEditarPage.tsx").read_text(encoding="utf-8")
    assert "/producto-editar/:id" in (raiz / "src/App.tsx").read_text(encoding="utf-8")


def test_formulario_que_solo_envia_react_native(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react-native")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "edad:int", "--solo", "crear"]) == 0
    assert main(["nuevo", "pantalla", "contacto", "--datos", "contacto", "--form"]) == 0
    pantalla = (raiz / "app/contacto.tsx").read_text(encoding="utf-8")
    assert "useFormulario" not in pantalla and "router.back" not in pantalla and "useLocalSearchParams" not in pantalla
    assert "<View key={enviados}>" in pantalla and "defaultValue" not in pantalla
    assert "import { Button, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';" in pantalla
    assert not (raiz / "hooks/useFormulario.ts").exists()


def test_los_pasos_del_servicio_segun_sus_funciones(en_carpeta, monkeypatch, capsys):
    _proyecto(en_carpeta, monkeypatch, "react")
    capsys.readouterr()  # lo que mostró crear
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", "crear"]) == 0
    salida = capsys.readouterr().out
    assert "nuevo pagina Contacto --datos contacto --form" in salida
    assert "--uno" not in salida and "useConsulta" not in salida
    # El mapa de lectura no muestra los hooks, que no se crearon.
    assert "src/hooks" not in salida


def test_la_lectura_no_muestra_los_hooks_que_el_servicio_no_usa(en_carpeta, monkeypatch, capsys):
    """Aunque existan (los creó otro servicio), un servicio --solo crear no los usa."""
    _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "--solo", "crear"]) == 0
    salida = capsys.readouterr().out
    assert "src/services/contactoService.ts" in salida and "src/hooks" not in salida
