"""Los formularios generados: el ejemplo del TODO(logica) usa un campo propio, y sin API el
error se entiende (no el "Failed to fetch" del navegador)."""

import pytest

from andamio.cli import main


def _proyecto(en_carpeta, monkeypatch, stack, *extra):
    assert main(["crear", stack, "web", *extra]) == 0
    raiz = en_carpeta / "web"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.mark.parametrize(
    "stack, extra, formulario, esperado",
    [
        ("react", [], "src/pages/libros/LibroFormPage.tsx", "String(datos.titulo).trim().length < 3"),
        ("react", ["--js"], "src/pages/libros/LibroFormPage.jsx", "String(datos.titulo).trim().length < 3"),
        ("next", [], "app/libros/LibroFormulario.tsx", "String(datos.titulo).trim().length < 3"),
        ("vue", [], "src/pages/libros/LibroFormPage.vue", "String(datos.value.titulo).trim().length < 3"),
    ],
)
def test_el_ejemplo_del_todo_usa_un_campo_del_formulario(en_carpeta, monkeypatch, stack, extra, formulario, esperado):
    raiz = _proyecto(en_carpeta, monkeypatch, stack, *extra)
    assert main(["nuevo", "crud", "libro", "titulo:str", "paginas:int"]) == 0
    texto = (raiz / formulario).read_text(encoding="utf-8")
    assert esperado in texto and "precio" not in texto


def test_el_ejemplo_de_un_numero(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "crud", "pago", "activo:bool", "monto:decimal"]) == 0
    texto = (raiz / "src/pages/pagos/PagoFormPage.tsx").read_text(encoding="utf-8")
    assert "if (Number(datos.monto) <= 0) { setErrores({ monto: ['Tiene que ser mayor que cero.'] }); return; }" in texto


def test_pagina_con_form_usa_los_campos_del_servicio(en_carpeta, monkeypatch):
    raiz = _proyecto(en_carpeta, monkeypatch, "react")
    assert main(["nuevo", "servicio", "contacto", "nombre:str", "email:email", "mensaje:text"]) == 0
    assert main(["nuevo", "pagina", "Contacto", "--datos", "contacto", "--form"]) == 0
    texto = (raiz / "src/pages/ContactoPage/ContactoPage.tsx").read_text(encoding="utf-8")
    assert "String(datos.nombre).trim().length < 3" in texto and "precio" not in texto


@pytest.mark.parametrize(
    "stack, extra, archivo",
    [
        ("react", [], "src/services/http.ts"),
        ("react", ["--js"], "src/services/http.js"),
        ("next", [], "services/http.ts"),
        ("vue", [], "src/services/http.js"),
        ("react-native", [], "services/http.ts"),
    ],
)
def test_sin_api_el_error_dice_que_no_se_pudo_conectar(en_carpeta, monkeypatch, stack, extra, archivo):
    raiz = _proyecto(en_carpeta, monkeypatch, stack, *extra)
    assert main(["nuevo", "servicio", "producto", "nombre:str"]) == 0
    texto = (raiz / archivo).read_text(encoding="utf-8")
    assert "No se pudo conectar con la API (${API_URL}). ¿Está en marcha?" in texto
    assert "} catch {" in texto
