"""El login de React generado funciona en un navegador real contra la API de Django con
`nuevo login`: registro, ingreso, sesión, salir, token vencido y rutas protegidas.

Necesita Django, Node y Playwright: --lento.
"""

import functools
import http.server
import threading
from pathlib import Path

import pytest

from andamio.cli import main

from .apis import api_en_marcha, puerto_libre
from .node import NPX, ejecutar, npm_install, requiere_node
from .test_crud_navegador import _SPA, requiere_playwright

SCRIPT = Path(__file__).with_name("login_navegador.js")


class _Archivos(http.server.SimpleHTTPRequestHandler):
    """Sirve los archivos de la web tal cual, sin escribir cada pedido en la consola."""

    def log_message(self, *args):
        pass

SCRIPT_OBLIGATORIO = Path(__file__).with_name("login_obligatorio_navegador.js")


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize(
    "variante, backend",
    # El mismo login de React con las tres APIs, y el de Vue ("vue").
    [("ts", "django"), ("js", "django"), ("ts", "fastapi"), ("ts", "express"), ("vue", "django")],
)
def test_login_en_el_navegador(variante, backend, en_carpeta, monkeypatch):
    if backend == "fastapi":
        pytest.importorskip("jwt")
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    recursos = [["pedido", "cliente:str", "total:decimal", "--protegido"]]
    with api_en_marcha(backend, en_carpeta, monkeypatch, recursos, cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        crear = ["crear", "vue", "web"] if variante == "vue" else ["crear", "react", "web", "--variante", variante]
        assert main(crear) == 0
        web = en_carpeta / "web"
        monkeypatch.chdir(web)
        assert main(["nuevo", "login"]) == 0
        assert main(["nuevo", "pagina", "Perfil", "--protegido"]) == 0
        assert main(["nuevo", "crud", "pedido", "cliente:str", "total:decimal", "--protegido"]) == 0
        npm_install(web)
        ejecutar([NPX, "vite", "build", "--logLevel", "error"], web, env={"VITE_API_URL": url_api})

        web_servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto_web), functools.partial(_SPA, directory=str(web / "dist")))
        threading.Thread(target=web_servidor.serve_forever, daemon=True).start()
        try:
            resultado = ejecutar(["node", str(SCRIPT), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        finally:
            web_servidor.shutdown()
        assert resultado.stdout.count("ok - ") == 11, resultado.stdout


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("frontend", ["react", "vue"])
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
        npm_install(web)
        ejecutar([NPX, "vite", "build", "--logLevel", "error"], web, env={"VITE_API_URL": url_api})

        web_servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto_web), functools.partial(_SPA, directory=str(web / "dist")))
        threading.Thread(target=web_servidor.serve_forever, daemon=True).start()
        try:
            resultado = ejecutar(["node", str(SCRIPT_OBLIGATORIO), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        finally:
            web_servidor.shutdown()
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
        assert resultado.stdout.count("ok - ") == 6, resultado.stdout
