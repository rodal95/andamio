"""Los comandos, piezas y opciones también se pueden escribir en inglés, y `comandos` los muestra."""

import pytest

from andamio import stacks
from andamio.acciones import ALIAS_PIEZAS, clave_de_pieza
from andamio.cli import ALIAS_ACCIONES, ALIAS_COMANDOS, main


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def test_create_new_y_opciones_en_ingles(en_carpeta, monkeypatch, capsys):
    assert main(["create", "django", "my-api", "--dry-run"]) == 0
    assert not (en_carpeta / "my-api").exists()
    assert main(["create", "django", "my-api"]) == 0
    monkeypatch.chdir(en_carpeta / "my-api")
    assert main(["new", "resource", "product", "name:str", "--plural", "products", "--protected"]) == 0
    assert "permission_classes = [IsAuthenticatedOrReadOnly]" in leer(en_carpeta / "my-api/products/views.py")
    assert main(["g", "login"]) == 0
    assert (en_carpeta / "my-api/cuentas/urls.py").is_file()
    capsys.readouterr()
    assert main(["templates", "export", "resource"]) == 0
    assert (en_carpeta / "my-api/.andamio/plantillas/django/recurso/LEEME.md").is_file()


def test_variant_y_page(en_carpeta, monkeypatch):
    assert main(["create", "react", "web", "--variant", "js"]) == 0
    monkeypatch.chdir(en_carpeta / "web")
    assert (en_carpeta / "web/src/App.jsx").is_file()
    assert main(["new", "page", "About"]) == 0
    assert main(["generate", "página", "Contacto"]) == 0  # con tilde también
    app = leer(en_carpeta / "web/src/App.jsx")
    assert 'path="/about"' in app and 'path="/contacto"' in app


def test_folder_en_react_native(en_carpeta, monkeypatch):
    assert main(["create", "react-native", "app"]) == 0
    monkeypatch.chdir(en_carpeta / "app")
    assert main(["new", "screen", "detalle", "--folder", "productos"]) == 0
    assert (en_carpeta / "app/app/productos/detalle.tsx").is_file()


def test_los_alias_de_piezas_existen():
    claves = {clave for stack in stacks.REGISTRO for clave in stack.piezas}
    for ingles, espanol in ALIAS_PIEZAS.items():
        assert espanol in claves, espanol
        assert clave_de_pieza(ingles) == espanol
        assert ingles not in claves  # un alias no puede tapar una pieza


def test_comandos_muestra_todo(capsys):
    assert main(["commands"]) == 0
    salida = capsys.readouterr().out
    for clave, alias in {**ALIAS_COMANDOS, **ALIAS_ACCIONES}.items():
        assert clave in salida, clave
        for a in alias:
            assert a in salida, a
    for opcion in ("--dry-run", "--variant", "--folder", "--migrate", "--protected", "--plural", "--js", "--ts"):
        assert opcion in salida, opcion
    for stack in stacks.REGISTRO:
        assert stack.clave in salida
        for pieza in stack.piezas:
            assert f"nuevo {pieza} " in salida, (stack.clave, pieza)
    assert "recurso  (resource)" in salida and "(sin nombre)" in salida


@pytest.mark.parametrize("argumentos", [["nuevo", "--help"], ["new", "--help"], ["create", "--help"]])
def test_la_ayuda_muestra_los_alias(argumentos, capsys):
    assert main(argumentos) == 0
    salida = capsys.readouterr().out
    assert "--dry-run" in salida
