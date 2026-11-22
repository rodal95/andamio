"""React: `nuevo login` (ingresar, registro, sesión) y `--protegido` en pagina y crud."""

import pytest

from andamio.cli import main


def _leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def web(en_carpeta, monkeypatch):
    assert main(["crear", "react", "web"]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    return raiz


def test_login_genera_la_sesion_y_las_paginas(web):
    assert main(["nuevo", "login"]) == 0
    for archivo in (
        "src/services/authService.ts",
        "src/services/http.ts",
        "src/sesion/sesion.ts",
        "src/sesion/RutaProtegida.tsx",
        "src/sesion/MenuSesion.tsx",
        "src/sesion/index.ts",
        "src/pages/IngresarPage/IngresarPage.tsx",
        "src/pages/RegistroPage/RegistroPage.tsx",
    ):
        assert (web / archivo).is_file(), archivo
    app = _leer(web / "src/App.tsx")
    for esperado in (
        "import { IngresarPage } from './pages/IngresarPage';",
        "import { RegistroPage } from './pages/RegistroPage';",
        "import { MenuSesion } from './sesion';",
        '<Route path="/ingresar" element={<IngresarPage />} />',
        '<Route path="/registro" element={<RegistroPage />} />',
        "<MenuSesion />",
    ):
        assert esperado in app, esperado
    sesion = _leer(web / "src/sesion/sesion.ts")
    assert "import { alVencerLaSesion, leerToken } from '../services/http';" in sesion
    assert "alVencerLaSesion(() => cambiar({ usuario: null, cargando: false }));" in sesion
    assert "useSyncExternalStore(suscribirse, () => estado)" in sesion
    # El login de la API de Django: el token, el registro y el usuario.
    servicio = _leer(web / "src/services/authService.ts")
    for ruta in ("'/token/'", "'/registro/'", "'/yo/'"):
        assert ruta in servicio
    # Registrarse también ingresa; la contraseña se repite.
    assert "await ingresar({ username: datos.username, password: datos.password });" in sesion
    assert "Las contraseñas no coinciden." in _leer(web / "src/pages/RegistroPage/RegistroPage.tsx")
    assert '<Link to="/registro">Registrarse</Link>' in _leer(web / "src/sesion/MenuSesion.tsx")


def test_login_sin_registro(web):
    assert main(["nuevo", "login", "--sin-registro"]) == 0
    assert not (web / "src/pages/RegistroPage").exists()
    app = _leer(web / "src/App.tsx")
    assert "RegistroPage" not in app and "/registro" not in app
    assert "/registro" not in _leer(web / "src/sesion/MenuSesion.tsx")
    ingresar = _leer(web / "src/pages/IngresarPage/IngresarPage.tsx")
    assert "import { Navigate, useLocation } from 'react-router';" in ingresar and "/registro" not in ingresar


def test_login_una_sola_vez_y_sin_nombre(web, capsys):
    assert main(["nuevo", "login", "cuenta"]) == 1
    assert "no lleva nombre" in capsys.readouterr().err
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "login"]) == 1


def test_login_sin_guia(web):
    assert main(["nuevo", "login", "--sin-guia"]) == 0
    sesion = _leer(web / "src/sesion/sesion.ts")
    assert "guía" not in sesion and "Si la API responde 401" not in sesion
    assert "alVencerLaSesion(() =>" in sesion
    assert "TODO(logica)" in _leer(web / "src/pages/RegistroPage/RegistroPage.tsx")


def test_login_con_un_http_anterior(web, capsys):
    """Un http de una versión anterior (sin alVencerLaSesion) no se toca: la sesión no lo
    usa (compila igual) y los pasos explican qué agregar."""
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    http = web / "src/services/http.ts"
    texto = _leer(http)
    inicio = texto.index("let alVencer")
    fin = texto.index("\n}\n", texto.index("export function alVencerLaSesion")) + 3
    texto = texto[:inicio] + texto[fin:]
    texto = texto.replace("  if (respuesta.status === 401 && leerToken()) {\n", "  if (false) {\n").replace("    alVencer?.();\n", "")
    http.write_text(texto, encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "login"]) == 0
    sesion = _leer(web / "src/sesion/sesion.ts")
    assert "import { leerToken } from '../services/http';" in sesion and "alVencerLaSesion" not in sesion
    assert "es de una versión anterior" in capsys.readouterr().out


def test_pagina_protegida_necesita_el_login(web, capsys):
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 1
    assert "nuevo login" in capsys.readouterr().err
    assert not (web / "src/pages/PerfilPage").exists()


def test_paginas_protegidas(web):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    assert main(["nuevo", "pagina", "Pedidos", "--protegido"]) == 0
    assert main(["nuevo", "pagina", "Ayuda"]) == 0
    app = _leer(web / "src/App.tsx")
    assert '<Route path="/perfil" element={<RutaProtegida><PerfilPage /></RutaProtegida>} />' in app
    assert '<Route path="/pedidos" element={<RutaProtegida><PedidosPage /></RutaProtegida>} />' in app
    assert '<Route path="/ayuda" element={<AyudaPage />} />' in app
    assert app.count("import { RutaProtegida } from './sesion';") == 1  # no se repite


def test_formulario_protegido_que_edita(web):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    assert main(["nuevo", "pagina", "ProductoEditar", "--datos", "producto", "--form", "--protegido"]) == 0
    app = _leer(web / "src/App.tsx")
    assert '<Route path="/producto-editar" element={<RutaProtegida><ProductoEditarPage /></RutaProtegida>} />' in app
    assert '<Route path="/producto-editar/:id" element={<RutaProtegida><ProductoEditarPage /></RutaProtegida>} />' in app


def test_crud_protegido(web):
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "crud", "producto", "nombre:str", "--protegido"]) == 0
    app = _leer(web / "src/App.tsx")
    assert '<Route path="/productos" element={<ProductoListaPage />} />' in app
    assert '<Route path="/productos/:id" element={<ProductoDetallePage />} />' in app
    assert '<Route path="/productos/nuevo" element={<RutaProtegida><ProductoFormPage /></RutaProtegida>} />' in app
    assert '<Route path="/productos/:id/editar" element={<RutaProtegida><ProductoFormPage /></RutaProtegida>} />' in app


def test_crud_sin_protegido_no_cambia(web):
    assert main(["nuevo", "crud", "producto", "nombre:str"]) == 0
    app = _leer(web / "src/App.tsx")
    assert '<Route path="/productos/nuevo" element={<ProductoFormPage />} />' in app
    assert "RutaProtegida" not in app


def test_login_en_javascript(en_carpeta, monkeypatch):
    assert main(["crear", "react", "web", "--js"]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", "login"]) == 0
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    for archivo in ("src/sesion/sesion.js", "src/sesion/RutaProtegida.jsx", "src/pages/IngresarPage/IngresarPage.jsx", "src/services/authService.js"):
        assert (raiz / archivo).is_file(), archivo
    assert "<RutaProtegida><PerfilPage /></RutaProtegida>" in _leer(raiz / "src/App.jsx")


def test_el_http_avisa_cuando_vence_la_sesion(web):
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    http = _leer(web / "src/services/http.ts")
    assert "export function alVencerLaSesion(funcion: () => void): void {" in http
    assert "if (respuesta.status === 401 && leerToken()) {" in http
