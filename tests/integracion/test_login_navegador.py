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


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("variante", ["ts", "js"])
def test_login_en_el_navegador(variante, en_carpeta, monkeypatch):
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    recursos = [["pedido", "cliente:str", "total:decimal", "--protegido"]]
    with api_en_marcha("django", en_carpeta, monkeypatch, recursos, cors=origen, previas=[["login"]]) as url_api:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", "react", "web", "--variante", variante]) == 0
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
