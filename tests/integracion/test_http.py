"""Archivos .http: peticiones de ejemplo para probar a mano cada API (nucleo/ejemplos.py).

Se generan con el recurso (Django, FastAPI, Express y Next.js full stack) y con el login
de Django. Con --lento, además se ejecutan contra la API generada en marcha.
"""

import importlib.util
import json
import re

import pytest

from andamio.cli import main

from .apis import BACKENDS, api_en_marcha, requiere
from .archivo_http import ejecutar

CAMPOS = ["nombre:str", "precio:decimal", "stock:int", "activo:bool", "alta:date"]


def _cuerpos(texto):
    return [json.loads(b) for b in re.findall(r"(?ms)^\{$.*?^\}$", texto)]


def _generar(en_carpeta, monkeypatch, stack, extra, *argumentos):
    assert main(["crear", stack, "api", *extra]) == 0
    raiz = en_carpeta / "api"
    monkeypatch.chdir(raiz)
    assert main(["nuevo", *argumentos]) == 0
    return raiz


@pytest.mark.parametrize(
    "stack, extra, url",
    [
        ("django", [], "http://127.0.0.1:8000/api"),
        ("fastapi", [], "http://127.0.0.1:8000/api"),
        ("express", [], "http://localhost:8000/api"),
        ("express", ["--js"], "http://localhost:8000/api"),
        ("next-fullstack", [], "http://localhost:3000/api"),
        ("next-fullstack", ["--js"], "http://localhost:3000/api"),
    ],
)
def test_el_recurso_trae_su_archivo_http(en_carpeta, monkeypatch, stack, extra, url):
    raiz = _generar(en_carpeta, monkeypatch, stack, extra, "recurso", "producto", *CAMPOS)
    texto = (raiz / "http/productos.http").read_text(encoding="utf-8")
    assert "@@" not in texto
    assert f"@api = {url}\n@base = {{{{api}}}}/productos" in texto
    for peticion in ("GET {{base}}/", "POST {{base}}/", "PUT {{base}}/1/", "PATCH {{base}}/1/", "DELETE {{base}}/1/"):
        assert peticion in texto
    crear, reemplazar, modificar = _cuerpos(texto)
    assert crear == {"nombre": "Texto de prueba", "precio": 10.5, "stock": 1, "activo": True, "alta": "2025-01-15"}
    assert reemplazar.keys() == crear.keys() and modificar == {"nombre": "Texto modificado"}
    assert "Authorization" not in texto  # sin --protegido no hace falta el token


def test_django_protegido_pide_el_token_antes(en_carpeta, monkeypatch):
    raiz = _generar(en_carpeta, monkeypatch, "django", [], "recurso", "producto", *CAMPOS, "--protegido")
    texto = (raiz / "http/productos.http").read_text(encoding="utf-8")
    assert "# @name login\nPOST {{api}}/token/" in texto
    assert texto.count("Authorization: Bearer {{token}}") == 4  # crear, reemplazar, modificar y eliminar
    assert texto.index("@token = {{login.response.body.access}}") < texto.index("### Crear uno")


def test_el_login_de_django_trae_su_archivo_http(en_carpeta, monkeypatch):
    raiz = _generar(en_carpeta, monkeypatch, "django", [], "login")
    texto = (raiz / "http/login.http").read_text(encoding="utf-8")
    for ruta in ("/registro/", "/token/", "/yo/", "/token/refresh/"):
        assert f"{{{{base}}}}{ruta}" in texto


@pytest.mark.lento
@pytest.mark.parametrize("backend", BACKENDS)
def test_las_peticiones_funcionan_contra_la_api(backend, tmp_path, monkeypatch):
    with api_en_marcha(backend, tmp_path, monkeypatch, [["producto", *CAMPOS]]) as url:
        texto = (tmp_path / "api/http/productos.http").read_text(encoding="utf-8")
        respuestas = ejecutar(texto, {"api": url})
    estados = {r.titulo.split(" (")[0]: r.estado for r in respuestas}
    assert estados == {
        "Listar todos": 200,
        "Buscar, ordenar y filtrar": 200,
        "Crear uno": 201,
        "Ver uno": 200,
        "Reemplazar todos los campos": 200,
        "Modificar solo algunos campos": 200,
        "Eliminar": 204,
    }, [(r.titulo, r.estado, r.cuerpo) for r in respuestas]


SIMPLEJWT = importlib.util.find_spec("rest_framework_simplejwt") is not None


@pytest.mark.lento
@pytest.mark.django
@requiere("django")
@pytest.mark.skipif(not SIMPLEJWT, reason="falta djangorestframework-simplejwt")
def test_login_y_recurso_protegido_contra_la_api(tmp_path, monkeypatch):
    protegido = [["producto", *CAMPOS, "--protegido"]]
    with api_en_marcha("django", tmp_path, monkeypatch, protegido, previas=[["login"]]) as url:
        raiz = tmp_path / "api"
        login = ejecutar((raiz / "http/login.http").read_text(encoding="utf-8"), {"base": url})
        assert [r.estado for r in login] == [201, 200, 200, 200], [(r.titulo, r.estado, r.cuerpo) for r in login]
        # El recurso protegido usa el usuario que se acaba de registrar.
        variables = {"api": url, "usuario": "alumno.prueba", "clave": "una-clave-bien-larga-2025"}
        recurso = ejecutar((raiz / "http/productos.http").read_text(encoding="utf-8"), variables)
    assert [r.estado for r in recurso] == [200, 200, 200, 201, 200, 200, 200, 204], [(r.titulo, r.estado) for r in recurso]
