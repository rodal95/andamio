"""Levanta una API generada por andamio (Django o FastAPI) para probar los frontends contra ella.

Las dos cumplen el mismo contrato, así que las mismas pruebas de React y React Native
se ejecutan contra cada una (parametrizadas con BACKENDS).
"""

from __future__ import annotations

import contextlib
import importlib.util
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from andamio.cli import main

DEPENDENCIAS = {
    "django": ["django", "rest_framework", "django_filters", "corsheaders", "drf_spectacular", "drf_spectacular_sidecar", "dotenv", "dj_database_url"],
    "fastapi": ["fastapi", "fastapi_offline", "sqlmodel", "uvicorn", "email_validator", "dotenv", "httpx2"],
}
INSTALAR = {
    "django": "pip install -r andamio/plantillas/django/_proyecto/requirements.txt",
    "fastapi": "pip install -r andamio/plantillas/fastapi/_proyecto/requirements.txt",
}


def requiere(backend: str) -> pytest.MarkDecorator:
    faltantes = [m for m in DEPENDENCIAS[backend] if importlib.util.find_spec(m) is None]
    return pytest.mark.skipif(bool(faltantes), reason=f"faltan dependencias de {backend}: {INSTALAR[backend]}")


# Para parametrizar: @pytest.mark.parametrize("backend", BACKENDS)
BACKENDS = [pytest.param(b, marks=[requiere(b), getattr(pytest.mark, b)], id=b) for b in DEPENDENCIAS]


def puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _comando_servidor(backend: str, puerto: int) -> list[str]:
    if backend == "django":
        return [sys.executable, "manage.py", "runserver", f"127.0.0.1:{puerto}", "--noreload"]
    return [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(puerto)]


@contextlib.contextmanager
def api_en_marcha(backend: str, carpeta: Path, monkeypatch, recursos: list[list[str]], cors: str | None = None):
    """Crea el proyecto `api` en `carpeta`, genera los recursos y lo pone en marcha.

    Devuelve la dirección de la API (http://127.0.0.1:<puerto>/api).
    """
    monkeypatch.chdir(carpeta)
    assert main(["crear", backend, "api"]) == 0
    raiz = carpeta / "api"
    monkeypatch.chdir(raiz)
    migrar = ["--migrar"] if backend == "django" else []
    for argumentos in recursos:
        assert main(["nuevo", "recurso", *argumentos, *migrar]) == 0
    monkeypatch.chdir(carpeta)

    puerto = puerto_libre()
    entorno = dict(os.environ)
    if cors:
        entorno["CORS_ALLOWED_ORIGINS"] = cors
    servidor = subprocess.Popen(
        _comando_servidor(backend, puerto), cwd=raiz, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=entorno
    )
    url = f"http://127.0.0.1:{puerto}/api"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(f"{url}/", timeout=2)
                break
            except urllib.error.HTTPError:
                break  # respondió, aunque sea con un error: ya está en marcha
            except OSError:
                if servidor.poll() is not None:
                    pytest.fail(f"La API de {backend} terminó al arrancar")
                time.sleep(0.5)
        else:
            pytest.fail(f"La API de {backend} no arrancó")
        yield url
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)
