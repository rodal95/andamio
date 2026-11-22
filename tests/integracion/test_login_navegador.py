"""El login de React generado funciona en un navegador real contra la API de Django con
`nuevo login`: registro, ingreso, sesión, salir, token vencido y rutas protegidas.

Necesita Django, Node y Playwright: --lento.
"""

import contextlib
import functools
import http.server
import subprocess
import threading
from pathlib import Path

import pytest

from andamio.cli import main

from .apis import NODE, api_en_marcha, puerto_libre
from .node import NPM, NPX, ejecutar, npm_install, requiere_node
from .test_crud_navegador import _SPA, requiere_playwright

SCRIPT = Path(__file__).with_name("login_navegador.js")


class _Archivos(http.server.SimpleHTTPRequestHandler):
    """Sirve los archivos de la web tal cual, sin escribir cada pedido en la consola."""

    def log_message(self, *args):
        pass

SCRIPT_OBLIGATORIO = Path(__file__).with_name("login_obligatorio_navegador.js")


@contextlib.contextmanager
def _next_en_marcha(web: Path, puerto: int, entorno: dict | None = None):
    """next build y next start en el puerto."""
    ejecutar([NPM, "run", "build"], web, env={"NEXT_TELEMETRY_DISABLED": "1", **(entorno or {})})
    servidor = subprocess.Popen(
        [NODE, "node_modules/next/dist/bin/next", "start", "-p", str(puerto), "-H", "127.0.0.1"], cwd=web, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        from .test_next import _esperar

        _esperar(f"http://127.0.0.1:{puerto}", servidor)
        yield
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


@contextlib.contextmanager
def _web_en_marcha(web: Path, frontend: str, puerto: int, url_api: str):
    """Compila la web (Vite o Next.js) con la dirección de la API y la sirve en el puerto."""
    npm_install(web)
    if frontend == "next":
        with _next_en_marcha(web, puerto, {"NEXT_PUBLIC_API_URL": url_api}):
            yield
        return
    ejecutar([NPX, "vite", "build", "--logLevel", "error"], web, env={"VITE_API_URL": url_api})
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto), functools.partial(_SPA, directory=str(web / "dist")))
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        yield
    finally:
        servidor.shutdown()


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize(
    "variante, backend",
    # El mismo login de React con las tres APIs, y el de Vue ("vue") y Next.js ("next", "next-js").
    [("ts", "django"), ("js", "django"), ("ts", "fastapi"), ("ts", "express"), ("vue", "django"), ("next", "django"), ("next-js", "express")],
)
def test_login_en_el_navegador(variante, backend, en_carpeta, monkeypatch):
    if backend == "fastapi":
        pytest.importorskip("jwt")
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    recursos = [["pedido", "cliente:str", "total:decimal", "--protegido"]]
    with api_en_marcha(backend, en_carpeta, monkeypatch, recursos, cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        crear = {
            "vue": ["crear", "vue", "web"],
            "next": ["crear", "next", "web"],
            "next-js": ["crear", "next", "web", "--variante", "js"],
        }.get(variante, ["crear", "react", "web", "--variante", variante])
        assert main(crear) == 0
        web = en_carpeta / "web"
        monkeypatch.chdir(web)
        assert main(["nuevo", "login"]) == 0
        assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
        assert main(["nuevo", "crud", "pedido", "cliente:str", "total:decimal", "--protegido"]) == 0
        with _web_en_marcha(web, "next" if variante.startswith("next") else "vite", puerto_web, url_api):
            resultado = ejecutar(["node", str(SCRIPT), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        assert resultado.stdout.count("ok - ") == 11, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("frontend", ["react", "vue", "next"])
def test_login_obligatorio_en_el_navegador(frontend, en_carpeta, monkeypatch):
    """nuevo login --obligatorio: sin sesión no se ve nada de la app (ni el menú, ni el pie)."""
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    # Un recurso cualquiera: con --migrar crea también las tablas del login (los usuarios).
    recursos = [["nota", "texto:str"]]
    with api_en_marcha("django", en_carpeta, monkeypatch, recursos, cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", frontend, "web"]) == 0
        web = en_carpeta / "web"
        monkeypatch.chdir(web)
        assert main(["nuevo", "login", "--obligatorio"]) == 0
        assert main(["nuevo", "pagina", "Nosotros"]) == 0
        assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
        with _web_en_marcha(web, "next" if frontend == "next" else "vite", puerto_web, url_api):
            resultado = ejecutar(["node", str(SCRIPT_OBLIGATORIO), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        assert resultado.stdout.count("ok - ") == 5, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
def test_login_de_la_web_en_el_navegador(en_carpeta, monkeypatch):
    """La web en HTML y JS (sin instalar nada): login, página --protegido y token vencido."""
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    with api_en_marcha("django", en_carpeta, monkeypatch, [["nota", "texto:str"]], cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", "web", "sitio"]) == 0
        web = en_carpeta / "sitio"
        monkeypatch.chdir(web)
        assert main(["nuevo", "login"]) == 0
        assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
        config = web / "js/config.js"
        config.write_text(config.read_text(encoding="utf-8").replace("http://localhost:8000/api", url_api), encoding="utf-8")

        servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto_web), functools.partial(_Archivos, directory=str(web)))
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            resultado = ejecutar(["node", str(Path(__file__).with_name("login_web_navegador.js")), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        finally:
            servidor.shutdown()
        assert resultado.stdout.count("ok - ") == 7, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
def test_login_de_react_native_en_el_navegador(en_carpeta, monkeypatch):
    """React Native en su versión web (react-native-web): login, pantalla --protegido, la
    sesión guardada al recargar y token vencido."""
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    with api_en_marcha("django", en_carpeta, monkeypatch, [["nota", "texto:str"]], cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", "react-native", "app"]) == 0
        app = en_carpeta / "app"
        monkeypatch.chdir(app)
        assert main(["nuevo", "login"]) == 0
        assert main(["nuevo", "pantalla", "perfil", "--protegido"]) == 0
        npm_install(app)
        ejecutar([NPX, "expo", "export", "--platform", "web"], app, env={"EXPO_PUBLIC_API_URL": url_api, "CI": "1"})

        servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto_web), functools.partial(_SPA, directory=str(app / "dist")))
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            resultado = ejecutar(["node", str(Path(__file__).with_name("login_rn_navegador.js")), origen], app, env={"NO_PROXY": "127.0.0.1,localhost"})
        finally:
            servidor.shutdown()
        assert resultado.stdout.count("ok - ") == 8, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("variante", ["ts", "js"])
def test_login_de_next_fullstack_en_el_navegador(variante, en_carpeta, monkeypatch):
    """Next.js full stack: la API propia con la cookie httpOnly, proxy.ts y recurso --protegido."""
    assert main(["crear", "next-fullstack", "app", "--variante", variante]) == 0
    app = en_carpeta / "app"
    monkeypatch.chdir(app)
    npm_install(app)
    assert main(["nuevo", "login", "--migrar"]) == 0
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    campos = ["cliente:str", "total:decimal", "--protegido"]
    assert main(["nuevo", "recurso", "pedido", *campos, "--migrar"]) == 0
    assert main(["nuevo", "crud", "pedido", *campos]) == 0
    pruebas = ejecutar([NPM, "test"], app)
    assert "# pass 14" in pruebas.stdout and "# fail 0" in pruebas.stdout, pruebas.stdout[-3000:]
    puerto = puerto_libre()
    with _next_en_marcha(app, puerto):
        resultado = ejecutar(["node", str(Path(__file__).with_name("login_fullstack_navegador.js")), f"http://127.0.0.1:{puerto}"], app, env={"NO_PROXY": "127.0.0.1,localhost"})
    assert resultado.stdout.count("ok - ") == 8, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
def test_login_obligatorio_de_next_fullstack(en_carpeta, monkeypatch):
    """--obligatorio en full stack: proxy.ts pide ingresar en todas las páginas."""
    assert main(["crear", "next-fullstack", "app"]) == 0
    app = en_carpeta / "app"
    monkeypatch.chdir(app)
    npm_install(app)
    assert main(["nuevo", "login", "--obligatorio", "--migrar"]) == 0
    assert main(["nuevo", "pagina", "Nosotros"]) == 0
    assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
    puerto = puerto_libre()
    with _next_en_marcha(app, puerto):
        resultado = ejecutar(["node", str(SCRIPT_OBLIGATORIO), f"http://127.0.0.1:{puerto}"], app, env={"NO_PROXY": "127.0.0.1,localhost"})
    assert resultado.stdout.count("ok - ") == 5, resultado.stdout
