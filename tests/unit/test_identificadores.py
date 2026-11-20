"""Qué identificadores declara una plantilla y cuándo un nombre choca con ellos."""

from andamio.nucleo.identificadores import CENTINELA, conflicto, declarados
from andamio.nucleo.motor import renderizar
from andamio.nucleo.nombres import Nombre


def _centinela(texto):
    return renderizar(texto, CENTINELA.marcadores())


def test_python_imports_funciones_variables_y_parametros():
    codigo = (
        "from app.db import Sesion as SesionBD\n"
        "import os\n"
        "class @@Nombre@@Base:\n    pass\n"
        "def buscar(bd: SesionBD, id_@@nombre@@: int):\n"
        "    consulta = 1\n"
        "    @@campos@@\n"
    )
    assert declarados("router.py", codigo) == {"SesionBD", "os", "buscar", "bd", "consulta"}


def test_javascript_imports_desestructuracion_y_parametros():
    codigo = """
import { useState, type ReactNode } from 'react';
import styles from './x.module.css';
export function @@Nombre@@Detalle({ @@nombreCamel@@, onEditar }: Props) {
  const [cargando, setCargando] = useState(false);
  const { data: datos } = usar();
  const manejar = (evento: Event, id: number) => {};
}
"""
    assert declarados("Detalle.tsx", codigo) == {
        "useState", "ReactNode", "styles", "onEditar", "cargando", "setCargando", "datos", "manejar", "evento", "id",
    }


def test_vue_solo_mira_el_script():
    codigo = '<template><p id="error">{{ error }}</p></template>\n<script setup>\nconst error = ref("");\n</script>\n'
    assert declarados("Pagina.vue", codigo) == {"error"}


def test_hay_conflicto_si_el_nombre_se_usa_en_el_mismo_archivo():
    plantilla = "def buscar(sesion, id):\n    @@nombre@@ = sesion.get(id)\n"
    assert conflicto("router.py", _centinela(plantilla), Nombre.desde_texto("sesion")) == "sesion"
    assert conflicto("router.py", _centinela(plantilla), Nombre.desde_texto("producto")) is None


def test_no_hay_conflicto_si_el_nombre_va_pegado_a_otra_palabra():
    # id_@@nombre@@ no es el nombre suelto: un recurso "buscar" no choca con def buscar.
    plantilla = "def buscar(id_@@nombre@@):\n    return id_@@nombre@@\n"
    assert conflicto("router.py", _centinela(plantilla), Nombre.desde_texto("buscar")) is None
