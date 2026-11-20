"""Barrido de nombres riesgosos (ver barrido.py): con cualquier nombre o campo que use el
código de las plantillas, andamio lo rechaza con un mensaje claro o genera código que
compila. Recorre todas las piezas de todos los stacks, así que es un test lento.

Para JavaScript, TypeScript y Vue necesita `typescript` en Node (npm install -g typescript);
sin eso, en esos stacks solo se controla lo demás (ids repetidos en el HTML).
"""

import pytest

from andamio import stacks

from .barrido import NOMBRE_DE_LISTA, barrer

CASOS = []
for _stack in stacks.REGISTRO:
    for _variante in list(_stack.variantes) or [""]:
        for _clave, _pieza in _stack.piezas.items():
            if _clave not in NOMBRE_DE_LISTA:
                CASOS.append(pytest.param(_stack.clave, _clave, _variante, False, id=f"{_stack.clave}-{_variante or 'unica'}-{_clave}-nombres"))
            if _pieza.usa_campos:
                CASOS.append(pytest.param(_stack.clave, _clave, _variante, True, id=f"{_stack.clave}-{_variante or 'unica'}-{_clave}-campos"))


@pytest.mark.lento
@pytest.mark.parametrize("stack, pieza, variante, campos", CASOS)
def test_ningun_nombre_genera_codigo_roto(stack, pieza, variante, campos, tmp_path):
    resultado = barrer(stack, pieza, tmp_path, variante, campos)
    assert resultado.generados, "no se generó nada: el barrido no probó la pieza"
    assert not resultado.problemas, f"{resultado.resumen()}\n" + "\n".join(resultado.problemas)
