"""El mapa de lectura: después de generar, en qué orden leer los archivos y qué hace cada uno."""

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo.campos import parsear_campo
from andamio.nucleo.generador import contexto_pieza, nombre_para_pieza
from andamio.nucleo.lectura import buscar_marcas, orden_de_lectura, texto_de_marca
from andamio.stacks.base import Solicitud

CASOS = [
    pytest.param(s, v, clave, id=f"{s.clave}-{v or 'unica'}-{clave}")
    for s in stacks.REGISTRO
    for v in (list(s.variantes) or [""])
    for clave, pieza in s.piezas.items()
    if pieza.lectura
]


@pytest.mark.parametrize("stack, variante, clave", CASOS)
def test_cada_archivo_del_orden_de_lectura_existe(stack, variante, clave, en_carpeta, monkeypatch, capsys):
    pieza = stack.piezas[clave]
    assert main(["crear", stack.clave, "proy", *(["--variante", variante] if variante else [])]) == 0
    raiz = en_carpeta / "proy"
    monkeypatch.chdir(raiz)
    nombre, *campos = pieza.ejemplo.split() or [pieza.nombre_defecto]
    for previo in pieza.preparar:
        assert main(["nuevo", *previo.split()]) == 0
    capsys.readouterr()
    assert main(["nuevo", clave, nombre, *campos]) == 0
    salida = capsys.readouterr().out
    assert "leé en este orden" in salida
    campos_sol = [parsear_campo(c, stack.tipos) for c in campos]
    sol = Solicitud(stack, pieza, raiz, nombre_para_pieza(pieza, nombre), campos_sol, variante=variante)
    for ruta, rol in orden_de_lectura(pieza.lectura, contexto_pieza(sol)):
        assert (raiz / ruta).is_file(), ruta
        assert "@@" not in ruta + rol
        assert ruta in salida


def test_las_marcas_de_logica_se_leen_sin_el_comentario():
    texto = "a = 1\n    # TODO(logica): validá que el precio sea positivo.\n{/* TODO(logica): mostrá un aviso */}\n"
    marcas = buscar_marcas(texto, "x.py")
    assert [(m.linea, m.texto) for m in marcas] == [(2, "validá que el precio sea positivo."), (3, "mostrá un aviso")]
    assert texto_de_marca("<!-- TODO(logica): algo -->") == "algo"


def test_simular_no_muestra_el_mapa(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "fastapi", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre:str", "--simular"]) == 0
    assert "leé en este orden" not in capsys.readouterr().out
