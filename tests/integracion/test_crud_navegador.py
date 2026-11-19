"""El CRUD generado funciona en un navegador real contra la API generada en Django.

Crea un recurso en Django y el CRUD con los mismos campos en React, compila la web y
la recorre con Chromium (Playwright): lista, agregar, detalle, editar, error de
validación de Django y eliminar. Necesita Django, Node y Playwright: --lento.
"""

import functools
import http.server
import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import pytest

from andamio.cli import main

from .node import NPX, ejecutar, npm_install, requiere_node
from .test_coherencia import CAMPOS, _puerto_libre
from .test_django import requiere_django

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
@pytest.mark.django
@requiere_django
@requiere_node
@requiere_playwright
@pytest.mark.parametrize("variante", ["ts", "js"])
def test_crud_en_el_navegador(variante, en_carpeta, monkeypatch):
    puerto_api, puerto_web = _puerto_libre(), _puerto_libre()
    while puerto_web == puerto_api:
        puerto_web = _puerto_libre()

    assert main(["crear", "django", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    assert main(["nuevo", "recurso", "producto", *CAMPOS, "--migrar"]) == 0
    servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{puerto_api}", "--noreload"],
        cwd=en_carpeta / "api",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "CORS_ALLOWED_ORIGINS": f"http://127.0.0.1:{puerto_web}"},
    )
    web_servidor = None
    try:
        monkeypatch.chdir(en_carpeta)
        assert main(["crear", "react", "web", "--variante", variante]) == 0
        web = en_carpeta / "web"
        monkeypatch.chdir(web)
        assert main(["nuevo", "crud", "producto", *CAMPOS]) == 0
        npm_install(web)
        ejecutar([NPX, "vite", "build", "--logLevel", "error"], web, env={"VITE_API_URL": f"http://127.0.0.1:{puerto_api}/api"})

        web_servidor = http.server.ThreadingHTTPServer(
            ("127.0.0.1", puerto_web), functools.partial(_SPA, directory=str(web / "dist"))
        )
        threading.Thread(target=web_servidor.serve_forever, daemon=True).start()
        for _ in range(60):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{puerto_api}/api/productos/", timeout=2)
                break
            except OSError:
                time.sleep(0.5)

        resultado = ejecutar(["node", str(SCRIPT), f"http://127.0.0.1:{puerto_web}"], web, env={"NO_PROXY": "127.0.0.1,localhost"})
        assert resultado.stdout.count("ok - ") == 10, resultado.stdout
    finally:
        if web_servidor:
            web_servidor.shutdown()
        servidor.terminate()
        servidor.wait(timeout=30)
