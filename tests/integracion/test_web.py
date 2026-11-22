"""Stack web: HTML, CSS y JavaScript sin instalar nada."""

import shutil
import subprocess

import pytest

from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

NODE = shutil.which("node")


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "web", "Mi Pagina"]) == 0
    raiz = en_carpeta / "mi-pagina"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_piezas(proyecto):
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    assert main(["nuevo", "componente", "Tarjeta"]) == 0
    assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    assert main(["nuevo", "crud", "producto", "nombre:str", "descripcion:text", "precio:decimal", "activo:bool", "publicado:datetime"]) == 0
    return proyecto


def test_estructura(proyecto):
    for archivo in ["index.html", "css/estilos.css", "js/menu.js", "js/config.js", "js/http.js", "js/inicio.js", "README.md"]:
        assert (proyecto / archivo).is_file(), archivo
    assert not (proyecto / "package.json").exists()
    assert buscar_proyecto(proyecto / "js")[0].clave == "web"


def test_piezas(con_piezas):
    raiz = con_piezas
    menu = leer(raiz / "js/menu.js")
    assert "{ href: 'contacto.html', texto: 'Contacto' },\n  { href: 'productos.html', texto: 'Productos' },\n  // --- andamio:enlaces" in menu
    assert '@import url("componentes/tarjeta.css");\n/* --- andamio:componentes' in leer(raiz / "css/estilos.css")
    assert "export function crearTarjeta(" in leer(raiz / "js/componentes/tarjeta.js")
    assert "export const clienteServicio = {" in leer(raiz / "js/servicios/clienteServicio.js")
    pagina = leer(raiz / "productos.html")
    assert '<input type="number" step="0.01" id="precio" name="precio" />' in pagina
    assert '<textarea id="descripcion" name="descripcion" rows="3"></textarea>' in pagina
    assert '<small class="error" id="error-activo"></small>' in pagina
    assert "<th>Descripcion</th>" not in pagina
    codigo = leer(raiz / "js/paginas/productos.js")
    assert "precio: 'decimal'," in codigo and "const COLUMNAS = ['nombre', 'precio', 'activo', 'publicado'];" in codigo
    assert (raiz / "js/servicios/productoServicio.js").is_file()


def test_el_crud_usa_el_servicio_que_ya_existe(proyecto, capsys):
    assert main(["nuevo", "servicio", "producto", "nombre"]) == 0
    antes = leer(proyecto / "js/servicios/productoServicio.js")
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    assert leer(proyecto / "js/servicios/productoServicio.js") == antes


def test_pagina_repetida_o_inicio(proyecto, capsys):
    assert main(["nuevo", "pagina", "index"]) == 1
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "pagina", "contacto"]) == 1


@pytest.mark.skipif(NODE is None, reason="no hay Node para revisar la sintaxis de JavaScript")
def test_el_javascript_es_valido(con_piezas):
    for archivo in con_piezas.rglob("*.js"):
        # --input-type=module: los archivos usan import/export.
        resultado = subprocess.run([NODE, "--input-type=module", "--check"], input=leer(archivo), capture_output=True, text=True)
        assert resultado.returncode == 0, f"{archivo}\n{resultado.stderr}"


# --- Pie, login y páginas protegidas --------------------------------------------------------


def test_menu_y_pie(en_carpeta, monkeypatch):
    assert main(["crear", "web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    assert '<footer class="pie" data-pie></footer>' in (raiz / "index.html").read_text(encoding="utf-8")
    assert "function dibujarPie()" in (raiz / "js/menu.js").read_text(encoding="utf-8")


def test_login_y_pagina_protegida(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 1
    assert "nuevo login" in capsys.readouterr().err
    assert main(["nuevo", "login"]) == 0
    for archivo in ("js/sesion.js", "ingresar.html", "registro.html", "js/paginas/ingresar.js", "js/paginas/registro.js"):
        assert (raiz / archivo).is_file(), archivo
    menu = (raiz / "js/menu.js").read_text(encoding="utf-8")
    assert "import { dibujarSesion } from './sesion.js';" in menu and "dibujarSesion(nav, ENLACES);" in menu
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    assert "await pedirIngreso();" in (raiz / "js/paginas/perfil.js").read_text(encoding="utf-8")
    assert "{ href: 'perfil.html', texto: 'Perfil', soloConSesion: true }," in (raiz / "js/menu.js").read_text(encoding="utf-8")


def test_login_obligatorio(en_carpeta, monkeypatch):
    assert main(["crear", "web", "sitio"]) == 0
    raiz = en_carpeta / "sitio"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "login", "--obligatorio", "--sin-registro"]) == 0
    menu = (raiz / "js/menu.js").read_text(encoding="utf-8")
    assert "import { dibujarSesion, pedirIngreso } from './sesion.js';" in menu and "\n  pedirIngreso();" in menu
    assert not (raiz / "registro.html").exists()
    assert "Registrate" not in (raiz / "ingresar.html").read_text(encoding="utf-8")
