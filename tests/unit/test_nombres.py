import pytest

from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import (
    Nombre,
    parece_plural,
    pluralizar_palabra,
    quitar_tildes,
    separar_palabras,
    validar_nombre,
    validar_nombre_campo,
)


@pytest.mark.parametrize(
    "texto",
    ["linea venta", "Línea venta", "línea-venta", "LineaVenta", "lineaVenta", "linea_venta", "  LÍNEA   VENTA  "],
)
def test_distintas_escrituras_dan_el_mismo_nombre(texto):
    nombre = Nombre.desde_texto(texto)
    assert nombre.pascal == "LineaVenta"
    assert nombre.snake == "linea_venta"
    assert nombre.camel == "lineaVenta"
    assert nombre.kebab == "linea-venta"


def test_marcadores_de_un_nombre():
    m = Nombre.desde_texto("línea venta").marcadores()
    assert m["Nombre"] == "LineaVenta"
    assert m["plural"] == "lineas_venta"
    assert m["Plural"] == "LineasVenta"
    assert m["pluralKebab"] == "lineas-venta"
    assert m["titulo"] == "Lineas venta"


def test_enie_se_convierte_en_ni():
    assert quitar_tildes("año") == "anio"
    assert separar_palabras("AÑO") == ["anio"]
    assert separar_palabras("Ñandú") == ["niandu"]
    assert quitar_tildes("pingüino") == "pinguino"


def test_siglas_y_numeros():
    assert separar_palabras("HTTPServer") == ["http", "server"]
    assert separar_palabras("producto2") == ["producto2"]
    assert separar_palabras("IVA21") == ["iva21"]


@pytest.mark.parametrize(
    "singular, plural",
    [
        ("producto", "productos"),
        ("cliente", "clientes"),
        ("lapiz", "lapices"),
        ("camion", "camiones"),
        ("mes", "meses"),
        ("ley", "leyes"),
        ("usuario", "usuarios"),
        ("pais", "paises"),
    ],
)
def test_plural(singular, plural):
    assert pluralizar_palabra(singular) == plural


def test_plural_de_nombre_compuesto_pluraliza_la_primera_palabra():
    assert Nombre.desde_texto("detalle pedido").plural == "detalles_pedido"


def test_plural_explicito():
    nombre = Nombre.desde_texto("pais", plural="Países")
    assert nombre.plural == "paises"
    assert nombre.con_plural("naciones").plural == "naciones"


def test_parece_plural():
    assert parece_plural(["productos"])
    assert parece_plural(["clientes", "vip"])
    assert not parece_plural(["producto"])
    assert not parece_plural(["mes"])


@pytest.mark.parametrize("texto", ["", "   ", "---"])
def test_nombre_vacio(texto):
    with pytest.raises(AndamioError):
        separar_palabras(texto)


def test_caracteres_invalidos_se_explican():
    with pytest.raises(AndamioError) as e:
        separar_palabras("producto!")
    assert "!" in e.value.mensaje
    assert "letras" in e.value.sugerencia


def test_no_empieza_con_numero():
    with pytest.raises(AndamioError, match="número"):
        separar_palabras("2producto")


@pytest.mark.parametrize("texto", ["class", "import", "def", "new", "function", "return"])
def test_palabras_reservadas(texto):
    with pytest.raises(AndamioError, match="reservada"):
        validar_nombre(Nombre.desde_texto(texto))


def test_reservados_del_stack():
    with pytest.raises(AndamioError, match="ya existe"):
        validar_nombre(Nombre.desde_texto("producto"), {"productos": "la app ya existe"})


@pytest.mark.parametrize("texto", ["id", "ID", "creado", "actualizado", "pk", "class"])
def test_campos_reservados(texto):
    with pytest.raises(AndamioError):
        validar_nombre_campo(texto)


def test_campo_se_normaliza():
    assert validar_nombre_campo("Precio Unitario") == "precio_unitario"
    assert validar_nombre_campo("añoFabricación") == "anio_fabricacion"
