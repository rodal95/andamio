"""Controles sobre las plantillas incorporadas de todos los stacks."""

import pytest

from andamio import stacks
from andamio.nucleo import plantillas
from andamio.nucleo.motor import marcadores_usados
from andamio.nucleo.nombres import MARCADORES_NOMBRE

MARCADORES_PROYECTO = {"carpeta", "proyecto", "proyecto_snake", "Proyecto", "proyectoTitulo"}


def _piezas():
    for stack in stacks.REGISTRO:
        for pieza in stack.piezas.values():
            yield pytest.param(stack, pieza, id=f"{stack.clave}-{pieza.clave}")


@pytest.mark.parametrize("stack, pieza", list(_piezas()))
def test_cada_marcador_de_una_pieza_esta_declarado(stack, pieza):
    """Si falla: agregá el marcador a `marcadores` de la Pieza (así aparece en el LEEME)."""
    declarados = set(MARCADORES_NOMBRE) | set(pieza.marcadores)
    carpeta = plantillas.carpeta_incorporada(stack.clave) / pieza.clave
    usados = set()
    for archivo in plantillas.leer_arbol(carpeta):
        usados |= marcadores_usados(archivo.ruta)
        if archivo.texto is not None:
            usados |= marcadores_usados(archivo.texto)
    for insercion in pieza.inserciones:
        usados |= marcadores_usados(insercion.archivo + insercion.texto + insercion.descripcion)
    assert usados - declarados == set()


@pytest.mark.parametrize("stack", stacks.REGISTRO, ids=lambda s: s.clave)
def test_cada_stack_tiene_plantilla_de_proyecto(stack):
    carpeta = plantillas.carpeta_incorporada(stack.clave) / plantillas.CARPETA_PROYECTO
    assert carpeta.is_dir()
    assert plantillas.leer_arbol(carpeta, ignorar_leeme=False)


@pytest.mark.parametrize("stack", stacks.REGISTRO, ids=lambda s: s.clave)
def test_cada_pieza_tiene_carpeta(stack):
    for pieza in stack.piezas:
        assert (plantillas.carpeta_incorporada(stack.clave) / pieza).is_dir(), pieza
