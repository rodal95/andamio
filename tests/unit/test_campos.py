import pytest

from andamio.nucleo.campos import Campo, parsear_campo, validar_campos
from andamio.nucleo.errores import AndamioError

TIPOS = {"str": "texto", "int": "entero", "float": "decimal"}


def test_campo_con_tipo():
    assert parsear_campo("Precio:FLOAT", TIPOS) == Campo("precio", "float")


def test_campo_sin_tipo_es_str():
    assert parsear_campo("nombre", TIPOS) == Campo("nombre", "str")


def test_tipo_invalido_lista_los_validos():
    with pytest.raises(AndamioError) as e:
        parsear_campo("precio:decimal", TIPOS)
    assert "str, int, float" in e.value.sugerencia


def test_tipo_vacio():
    with pytest.raises(AndamioError, match="falta el tipo"):
        parsear_campo("precio:", TIPOS)


def test_campos_repetidos():
    with pytest.raises(AndamioError, match="repetido"):
        validar_campos([Campo("a", "str"), Campo("a", "int")])


def test_titulo_del_campo():
    assert Campo("precio_unitario", "float").titulo == "Precio unitario"
