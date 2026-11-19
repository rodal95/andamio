"""El CRUD generado funciona en un navegador real contra la API generada (Django y FastAPI).

Crea un recurso en la API y el CRUD con los mismos campos en React, compila la web y
la recorre con Chromium (Playwright): lista, agregar, detalle, editar, error de
validación de la API y eliminar. Necesita la API, Node y Playwright: --lento.
"""

import functools
import http.server
import subprocess
import threading
from pathlib import Path

import pytest

from andamio.cli import main

from .apis import BACKENDS, api_en_marcha, puerto_libre
from .node import NPX, ejecutar, npm_install, requiere_node
from .test_coherencia import CAMPOS

SCRIPT = Path(__file__).with_name("crud_navegador.js")


def _hay_playwright() -> bool:
    try:
        return subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0
    except OSError:
        return False


requiere_playwright = pytest.mark.skipif(not _hay_playwright(), reason="no está Playwright para Node")


class _SPA(http.server.SimpleHTTPRequestHandler):
    """Sirve la web compilada; las rutas que no son archivos devuelven index.html."""

    def send_head(self):  # noqa: N802
        if not Path(self.translate_path(self.path)).exists():
            self.path = "/index.html"
        return super().send_head()

    def log_message(self, *args):
        pass


@pytest.mark.lento
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("variante", ["ts", "js"])
def test_crud_en_el_navegador(variante, backend, en_carpeta, monkeypatch):
    puerto_web = puerto_libre()
    origen = f"http://127.0.0.1:{puerto_web}"
    with api_en_marcha(backend, en_carpeta, monkeypatch, [["producto", *CAMPOS]], cors=origen) as url_api:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", "react", "web", "--variante", variante]) == 0
        web = en_carpeta / "web"
        monkeypatch.chdir(web)
        assert main(["nuevo", "crud", "producto", *CAMPOS]) == 0
        npm_install(web)
        ejecutar([NPX, "vite", "build", "--logLevel", "error"], web, env={"VITE_API_URL": url_api})

        web_servidor = http.server.ThreadingHTTPServer(("127.0.0.1", puerto_web), functools.partial(_SPA, directory=str(web / "dist")))
        threading.Thread(target=web_servidor.serve_forever, daemon=True).start()
        try:
            resultado = ejecutar(["node", str(SCRIPT), origen], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        finally:
            web_servidor.shutdown()
        assert resultado.stdout.count("ok - ") == 10, resultado.stdout
