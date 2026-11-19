"""El script que arma las demostraciones de la página funciona con la versión actual."""

import sys
import tempfile
from pathlib import Path

import andamio
from andamio import stacks

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))
import sitio  # noqa: E402


def test_demostraciones_de_todos_los_stacks():
    datos = sitio.generar()
    assert datos["version"] == andamio.__version__
    assert {s["clave"] for s in datos["stacks"]} == {s.clave for s in stacks.REGISTRO}
    for stack in datos["stacks"]:
        rutas = {a["ruta"] for a in stack["archivos"]}
        assert stack["destacado"] in rutas, stack["clave"]
        assert any(a["estado"] == "nuevo" for a in stack["archivos"])
        assert all("Error" not in p["salida"] for p in stack["pasos"]), stack["pasos"]
        assert all("Listo." in p["salida"] for p in stack["pasos"])
    texto = str(datos)
    temporal = Path(tempfile.gettempdir()).resolve()
    assert str(temporal) not in texto and tempfile.gettempdir() not in texto, "no se tienen que ver rutas temporales"
    assert "SECRET_KEY=(se genera al azar" in texto


def test_sesion_del_menu():
    eventos = sitio.generar()["menu"]
    entradas = [e for e in eventos if e["tipo"] == "entrada"]
    assert entradas, "el menú tiene que pedir datos"
    salida = "".join(e["texto"] for e in eventos if e["tipo"] == "salida")
    assert "Proyecto Django REST detectado." in salida
    assert "Listo." in salida
    assert "C:\\Users\\alumno\\mi-api" in salida
