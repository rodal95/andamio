"""Stack vue: Vue 3 + Vite + Vue Router."""

import json

import pytest

from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .node import NPM, ejecutar, npm_install, requiere_node


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "vue", "Mi Web"]) == 0
    raiz = en_carpeta / "mi-web"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.fixture
def con_piezas(proyecto):
    assert main(["nuevo", "componente", "Tarjeta"]) == 0
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    assert main(["nuevo", "composable", "useContador"]) == 0
    assert main(["nuevo", "servicio", "cliente", "nombre", "email:email"]) == 0
    assert main(["nuevo", "crud", "producto", "nombre:str", "descripcion:text", "precio:decimal", "activo:bool", "publicado:datetime"]) == 0
    assert main(["nuevo", "crud", "medicion", "valor:float"]) == 0
    return proyecto


def test_estructura(proyecto):
    paquete = json.loads(leer(proyecto / "package.json"))
    assert {"vue", "vue-router"} <= set(paquete["dependencies"])
    assert buscar_proyecto(proyecto / "src")[0].clave == "vue"
    assert (proyecto / ".env").is_file()


def test_piezas(con_piezas):
    raiz = con_piezas
    assert (raiz / "src/components/Tarjeta.vue").is_file()
    assert "export function useContador(" in leer(raiz / "src/composables/useContador.js")
    # El menú está en TheNavbar.vue (lo muestra App.vue, con el pie).
    router, app = leer(raiz / "src/router.js"), leer(raiz / "src/components/TheNavbar.vue")
    assert "import ContactoPage from './pages/ContactoPage.vue';" in router
    assert "{ path: '/productos/:id/editar', component: ProductoFormPage }," in router
    assert '<RouterLink to="/productos">Productos</RouterLink>' in app
    formulario = leer(raiz / "src/pages/productos/ProductoFormPage.vue")
    assert '<input v-model.number="datos.precio" type="number" step="0.01" required />' in formulario
    assert "publicado: registro.publicado.slice(0, 16)," in formulario
    assert "{{ item.nombre }}" in leer(raiz / "src/pages/productos/ProductoListaPage.vue")
    assert "{{ `Medicion ${item.id}` }}" in leer(raiz / "src/pages/mediciones/MedicionListaPage.vue")


@pytest.mark.parametrize("argumentos", [["componente", "RouterLink"], ["composable", "route"], ["pagina", "app"]])
def test_nombres_que_no_se_pueden_usar(proyecto, argumentos):
    assert main(["nuevo", *argumentos]) == 1


def test_ruta_repetida(proyecto, capsys):
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    capsys.readouterr()
    assert main(["nuevo", "pagina", "contacto"]) == 1
    assert "Ya hay una página en la ruta /contacto" in capsys.readouterr().err


@pytest.mark.lento
@requiere_node
def test_npm_install_y_build(con_piezas):
    npm_install(con_piezas)
    ejecutar([NPM, "run", "build"], con_piezas)
    assert (con_piezas / "dist/index.html").is_file()


# --- Menú y pie; login; páginas protegidas ------------------------------------------------


def test_menu_y_pie(en_carpeta, monkeypatch):
    assert main(["crear", "vue", "web"]) == 0
    raiz = en_carpeta / "web"
    app = leer(raiz / "src/App.vue")
    assert '<TheNavbar v-if="!ruta.meta.sinMenu" />' in app and '<TheFooter v-if="!ruta.meta.sinMenu" />' in app
    assert "andamio:enlaces" in leer(raiz / "src/components/TheNavbar.vue")
    assert '<footer class="pie">' in leer(raiz / "src/components/TheFooter.vue")


def test_login_y_paginas_protegidas(en_carpeta, monkeypatch, capsys):
    assert main(["crear", "vue", "web"]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 1
    assert "nuevo login" in capsys.readouterr().err
    assert main(["nuevo", "login"]) == 0
    for archivo in ("src/sesion/sesion.js", "src/services/authService.js", "src/pages/IngresarPage.vue", "src/pages/RegistroPage.vue", "src/components/MenuSesion.vue"):
        assert (raiz / archivo).is_file(), archivo
    router = leer(raiz / "src/router.js")
    assert "{ path: '/ingresar', component: IngresarPage, meta: { publica: true } }," in router
    assert "router.beforeEach(async (destino) => {" in router and "destino.meta.protegida && !sesion.usuario" in router
    navbar = leer(raiz / "src/components/TheNavbar.vue")
    assert "import MenuSesion from './MenuSesion.vue';" in navbar and "<MenuSesion />" in navbar
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    assert main(["nuevo", "crud", "pedido", "total:decimal", "--protegido"]) == 0
    router = leer(raiz / "src/router.js")
    assert "{ path: '/perfil', component: PerfilPage, meta: { protegida: true } }," in router
    assert "{ path: '/pedidos/nuevo', component: PedidoFormPage, meta: { protegida: true } }," in router
    assert "{ path: '/pedidos', component: PedidoListaPage }," in router  # la lista es libre
    assert '<RouterLink to="/perfil">Perfil</RouterLink>' in leer(raiz / "src/components/MenuSesion.vue")
    assert "/perfil" not in leer(raiz / "src/components/TheNavbar.vue")


def test_login_obligatorio(en_carpeta, monkeypatch):
    assert main(["crear", "vue", "web"]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "login", "--obligatorio", "--sin-registro"]) == 0
    router = leer(raiz / "src/router.js")
    assert "{ path: '/ingresar', component: IngresarPage, meta: { publica: true, sinMenu: true } }," in router
    assert "!destino.meta.publica && !sesion.usuario" in router
    assert "RegistroPage" not in router and not (raiz / "src/pages/RegistroPage.vue").exists()
