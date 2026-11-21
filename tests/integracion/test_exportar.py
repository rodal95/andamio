"""andamio plantillas exportar y uso de las plantillas exportadas."""

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo import plantillas
from andamio.nucleo.generador import carpeta_pieza
from andamio.nucleo.nombres import MARCADORES_NOMBRE


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto_python(en_carpeta, monkeypatch):
    main(["crear", "python", "tienda"])
    raiz = en_carpeta / "tienda"
    monkeypatch.chdir(raiz)
    return raiz


@pytest.mark.parametrize("stack", stacks.REGISTRO, ids=lambda s: s.clave)
def test_exporta_todas_las_piezas_con_su_leeme(stack, en_carpeta, monkeypatch, capsys):
    main(["crear", stack.clave, "proyecto"])
    raiz = en_carpeta / "proyecto"
    monkeypatch.chdir(raiz)
    capsys.readouterr()
    assert main(["plantillas", "exportar"]) == 0
    assert "LEEME.md" in capsys.readouterr().out
    for clave, pieza in stack.piezas.items():
        carpeta = raiz / ".andamio" / "plantillas" / stack.clave / clave
        leeme = leer(carpeta / "LEEME.md")
        assert f"andamio nuevo {clave} {pieza.ejemplo}".rstrip() in leeme
        for marcador in {**MARCADORES_NOMBRE, **pieza.marcadores}:
            assert f"`@@{marcador}@@`" in leeme, marcador
        if "## Además" in leeme:
            assert "@@" not in leeme.split("## Además")[1]
        if plantillas.leer_arbol(carpeta_pieza(stack, pieza, next(iter(stack.variantes), ""))):  # busqueda y accion solo agregan
            assert any(p.name != "LEEME.md" for p in carpeta.rglob("*") if p.is_file())


def test_reexportar_no_pisa_nada(proyecto_python, capsys):
    main(["plantillas", "exportar"])
    plantilla = proyecto_python / ".andamio/plantillas/python/entidad/entidades/@@nombre@@.py"
    plantilla.write_text("# mi versión\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["plantillas", "exportar"]) == 0
    assert "ya estaban exportadas" in capsys.readouterr().out
    assert leer(plantilla) == "# mi versión\n"


def test_reexportar_no_devuelve_archivos_borrados(en_carpeta, monkeypatch, capsys):
    # Borrar un archivo de las plantillas exportadas es la forma de que no se genere:
    # exportar de nuevo no lo tiene que volver a crear.
    assert main(["crear", "django", "api"]) == 0
    monkeypatch.chdir(en_carpeta / "api")
    assert main(["plantillas", "exportar", "recurso"]) == 0
    admin = en_carpeta / "api/.andamio/plantillas/django/recurso/@@plural@@/admin.py"
    admin.unlink()
    capsys.readouterr()
    assert main(["plantillas", "exportar"]) == 0
    salida = capsys.readouterr().out
    assert not admin.exists()
    assert (en_carpeta / "api/.andamio/plantillas/django/login/LEEME.md").is_file()  # la otra pieza sí se exportó
    assert "Ya estaban exportadas y no se tocaron: recurso" in salida


def test_exportar_una_pieza(en_carpeta, monkeypatch, capsys):
    main(["crear", "react", "web"])
    monkeypatch.chdir(en_carpeta / "web")
    assert main(["plantillas", "exportar", "hook"]) == 0
    base = en_carpeta / "web/.andamio/plantillas/react"
    assert (base / "hook").is_dir()
    assert not (base / "componente").exists()
    capsys.readouterr()
    assert main(["plantillas", "exportar", "volador"]) == 1
    assert "Piezas disponibles" in capsys.readouterr().err


def test_las_plantillas_exportadas_se_usan(proyecto_python, capsys):
    main(["plantillas", "exportar", "entidad"])
    carpeta = proyecto_python / ".andamio/plantillas/python/entidad"
    plantilla = carpeta / "entidades/@@nombre@@.py"
    plantilla.write_text("# Tabla @@plural@@ (versión del alumno)\n" + leer(plantilla), encoding="utf-8")
    (carpeta / "menus/menu_@@nombre@@.py").unlink()
    capsys.readouterr()
    assert main(["nuevo", "entidad", "producto", "nombre"]) == 0
    assert "tus plantillas" in capsys.readouterr().out
    assert leer(proyecto_python / "entidades/producto.py").startswith("# Tabla productos (versión del alumno)\n")
    # Si borrás un archivo de la plantilla, deja de generarse.
    assert not (proyecto_python / "menus/menu_producto.py").exists()
    # Las inserciones siguen funcionando igual.
    assert "from menus import menu_producto" in leer(proyecto_python / "main.py")


def test_leeme_de_django_muestra_las_modificaciones(en_carpeta, monkeypatch):
    main(["crear", "django", "api"])
    monkeypatch.chdir(en_carpeta / "api")
    main(["plantillas", "exportar"])
    leeme = leer(en_carpeta / "api/.andamio/plantillas/django/recurso/LEEME.md")
    assert "`config/urls.py`: rutas /api/productos/" in leeme
    assert '  nombre = models.CharField("Nombre", max_length=200)' in leeme


def test_exportar_fuera_de_un_proyecto(en_carpeta, capsys):
    assert main(["plantillas", "exportar"]) == 1
    assert "No encontré un proyecto" in capsys.readouterr().err
