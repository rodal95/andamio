from pathlib import PurePosixPath

import pytest

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.motor import renderizar, renderizar_ruta


def test_reemplazo_simple():
    assert renderizar("class @@Nombre@@:", {"Nombre": "Producto"}) == "class Producto:"


def test_no_toca_template_literals_ni_jsx():
    texto = "const url = `${API}/@@plural@@/`;\n<View style={{ flex: 1 }} />\n"
    assert renderizar(texto, {"plural": "productos"}) == "const url = `${API}/productos/`;\n<View style={{ flex: 1 }} />\n"


def test_marcador_solo_en_linea_hereda_la_sangria():
    texto = "class A:\n    @@campos@@\n    fin = 1\n"
    resultado = renderizar(texto, {"campos": "a = 1\nb = 2\n\nc = 3"})
    assert resultado == "class A:\n    a = 1\n    b = 2\n\n    c = 3\n    fin = 1\n"


def test_valor_vacio_elimina_la_linea():
    assert renderizar("a\n    @@opcional@@\nb\n", {"opcional": ""}) == "a\nb\n"


def test_respeta_crlf():
    resultado = renderizar("x\r\n  @@v@@\r\ny\r\n", {"v": "1\n2"})
    assert resultado == "x\r\n  1\r\n  2\r\ny\r\n"


def test_una_sola_pasada():
    # Un valor que contiene un marcador no se vuelve a procesar.
    assert renderizar("@@a@@ @@b@@", {"a": "@@b@@", "b": "B"}) == "@@b@@ B"


def test_marcador_desconocido_es_error_con_sugerencia():
    with pytest.raises(AndamioError) as e:
        renderizar("@@Nombr@@", {"Nombre": "X"}, origen="pieza/archivo.py")
    assert "@@Nombr@@" in e.value.mensaje
    assert "pieza/archivo.py" in e.value.mensaje
    assert "@@Nombre@@" in e.value.sugerencia


def test_arrobas_sueltas_no_son_marcadores():
    texto = "@decorador\nemail@dominio.com\nx @@ y\n"
    assert renderizar(texto, {}) == texto


def test_ruta_con_marcadores():
    ruta = renderizar_ruta(("src", "@@Nombre@@", "@@Nombre@@.tsx"), {"Nombre": "Boton"})
    assert ruta == PurePosixPath("src/Boton/Boton.tsx")


def test_ruta_con_subcarpetas_y_partes_vacias():
    contexto = {"carpeta": "(tabs)/productos", "vacia": ""}
    assert renderizar_ruta(("app", "@@carpeta@@", "@@vacia@@", "x.tsx"), contexto) == PurePosixPath("app/(tabs)/productos/x.tsx")


def test_ruta_no_puede_salir_del_proyecto():
    with pytest.raises(AndamioError):
        renderizar_ruta(("@@x@@", "a.txt"), {"x": "../.."})
