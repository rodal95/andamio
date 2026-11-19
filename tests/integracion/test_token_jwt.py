"""El http de React, Vue y Next.js manda el token del login JWT (para los recursos --protegido)."""

import pytest

from andamio.cli import main

CASOS = [
    ("react", "ts", "src/services/http.ts"),
    ("react", "js", "src/services/http.js"),
    ("vue", "", "src/services/http.js"),
    ("next", "ts", "services/http.ts"),
    ("next", "js", "services/http.js"),
    ("next-fullstack", "ts", "services/http.ts"),
]


@pytest.mark.parametrize("pieza", ["crud", "servicio"])
@pytest.mark.parametrize("clave, variante, ruta", CASOS, ids=lambda v: v or "-")
def test_http_manda_el_token(clave, variante, ruta, pieza, en_carpeta, monkeypatch):
    assert main(["crear", clave, "web", *(["--variante", variante] if variante else [])]) == 0
    monkeypatch.chdir(en_carpeta / "web")
    assert main(["nuevo", pieza, "producto", "nombre:str", "precio:decimal"]) == 0
    http = (en_carpeta / "web" / ruta).read_text(encoding="utf-8")
    for esperado in ("export function guardarToken(", "export function borrarToken(", "export function leerToken(",
                     "resultado.Authorization = `Bearer ${token}`;", "headers: encabezados(datos),",
                     "typeof localStorage === 'undefined'", "'detail' in detalle"):  # fmt: skip
        assert esperado in http, (clave, variante, esperado)
    # La misma clave que la web HTML: el token sirve para todas las webs de andamio.
    assert "const CLAVE_TOKEN = 'token';" in http
