"""Stack reflex: aplicación hecha solo con Python, con base propia o usando una API de andamio."""

import importlib.util
import os
import py_compile
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .apis import api_en_marcha, puerto_libre, requiere
from .node import ejecutar, requiere_node
from .test_coherencia import CAMPOS
from .test_crud_navegador import requiere_playwright

SCRIPT = Path(__file__).with_name("crud_reflex.js")
HAY_REFLEX = importlib.util.find_spec("reflex") is not None
requiere_reflex = pytest.mark.skipif(
    not HAY_REFLEX, reason="falta Reflex: pip install -r andamio/plantillas/reflex/_proyecto/requirements.txt"
)


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


@pytest.fixture
def proyecto(en_carpeta, monkeypatch):
    assert main(["crear", "reflex", "Mi App"]) == 0
    monkeypatch.chdir(en_carpeta / "mi-app")
    return en_carpeta / "mi-app"


def test_estructura_del_proyecto(proyecto):
    archivos = {p.relative_to(proyecto).as_posix() for p in proyecto.rglob("*") if p.is_file()}
    assert archivos == {
        ".env",
        ".env.example",
        ".gitignore",
        "andamio-guia.html",
        "README.md",
        "requirements.txt",
        "rxconfig.py",
        "assets/.gitkeep",
        "mi_app/__init__.py",
        "mi_app/mi_app.py",
        "mi_app/plantilla.py",
        "mi_app/validacion.py",
        "mi_app/paginas/__init__.py",
        "mi_app/paginas/inicio.py",
    }
    config = leer(proyecto / "rxconfig.py")
    assert 'app_name="mi_app"' in config and "telemetry_enabled=False" in config  # sin datos de uso
    assert "backend_port=8001" in config  # el 8000 queda para las APIs de andamio
    assert "reflex[db]==" in leer(proyecto / "requirements.txt")
    assert "rx.Model" not in "".join(leer(p) for p in proyecto.rglob("*.py"))  # obsoleto desde Reflex 0.9.2
    for archivo in proyecto.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo), archivo
    for archivo in proyecto.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)


@pytest.mark.parametrize("nombre", ["reflex", "2024 app", "class"])
def test_nombres_de_proyecto_que_no_sirven(en_carpeta, capsys, nombre):
    assert main(["crear", "reflex", nombre]) == 1
    assert not any(en_carpeta.iterdir())


def test_piezas(proyecto):
    for argumentos in (
        ["crud", "producto", *CAMPOS],
        ["crud-api", "cliente", "nombre", "email:email"],
        ["pagina", "Contacto"],
        ["componente", "Tarjeta"],
        ["estado", "ContadorState"],
        ["servicio", "marca", "nombre"],
    ):
        assert main(["nuevo", *argumentos]) == 0, argumentos
    app = leer(proyecto / "mi_app/mi_app.py")
    assert "from mi_app.paginas.productos import ProductoState, productos" in app
    assert 'app.add_page(productos, route="/productos", title="Productos", on_load=ProductoState.cargar)' in app
    assert 'app.add_page(contacto, route="/contacto", title="Contacto")' in app
    menu = leer(proyecto / "mi_app/plantilla.py")
    assert '("Productos", "/productos"),\n    ("Clientes", "/clientes"),\n    ("Contacto", "/contacto"),' in menu
    modelo = leer(proyecto / "mi_app/modelos/producto.py")
    for esperado in (
        "class Producto(ProductoDatos, table=True):",
        "precio: Decimal = Field(max_digits=10, decimal_places=2)",
        "publicado: FechaHora",
        "from mi_app.validacion import FechaHora",
        "from datetime import UTC, date, datetime",
    ):
        assert esperado in modelo, esperado
    pagina = leer(proyecto / "mi_app/paginas/productos.py")
    assert 'rx.input(\n                id="precio",\n                type="number",\n                step="0.01",' in pagina
    assert '"publicado": producto.publicado.astimezone().strftime("%Y-%m-%dT%H:%M"),' in pagina
    clientes = leer(proyecto / "mi_app/paginas/clientes.py")
    assert "import mi_app.servicios.cliente as cliente_api" in clientes and "rx.session" not in clientes
    assert (proyecto / "mi_app/estados/contador.py").is_file()  # "ContadorState" -> contador
    assert 'RUTA = "/marcas/"' in leer(proyecto / "mi_app/servicios/marca.py")
    for archivo in proyecto.rglob("*.py"):
        py_compile.compile(str(archivo), doraise=True)
        assert "@@" not in leer(archivo), archivo


def test_crud_y_crud_api_no_se_pisan(proyecto, capsys):
    assert main(["nuevo", "crud", "producto", "nombre"]) == 0
    antes = {p: p.read_bytes() for p in proyecto.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert main(["nuevo", "crud-api", "producto", "nombre"]) == 1
    assert "productos.py" in capsys.readouterr().err
    assert antes == {p: p.read_bytes() for p in proyecto.rglob("*") if p.is_file()}


@pytest.mark.parametrize("campo", ["json", "model_config", "id"])
def test_campos_reservados(proyecto, capsys, campo):
    assert main(["nuevo", "crud", "producto", campo]) == 1


def test_sin_app_name(proyecto, capsys):
    (proyecto / "rxconfig.py").write_text("import reflex as rx\nconfig = rx.Config()\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["nuevo", "pagina", "Contacto"]) == 1
    assert "app_name" in capsys.readouterr().err


def test_deteccion(proyecto):
    reflex = stacks.por_clave("reflex")
    for carpeta in (proyecto, proyecto / "mi_app", proyecto / "mi_app/paginas"):
        assert buscar_proyecto(carpeta) == (reflex, proyecto)


def test_menu(en_carpeta, respuestas):
    respuestas(["12", "mi app", "s"])
    assert main([]) == 0
    assert (en_carpeta / "mi-app/rxconfig.py").is_file()


@pytest.mark.skipif(HAY_REFLEX, reason="este Python tiene Reflex: --migrar migraría de verdad")
def test_migrar_sin_reflex(proyecto, capsys, monkeypatch):
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre", "--migrar"]) == 1
    assert "reflex db init" in capsys.readouterr().err
    assert (proyecto / "mi_app/modelos/producto.py").is_file()  # los archivos se generan igual


# --- Con Reflex y Node: migraciones y la aplicación en el navegador -------------------------


def _esperar(url: str, proceso: subprocess.Popen, segundos: int = 600) -> None:
    for _ in range(segundos):
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except OSError:
            if proceso.poll() is not None:
                pytest.fail("reflex run terminó al arrancar")
            time.sleep(1)
    pytest.fail(f"No respondió {url}")


@pytest.mark.lento
@requiere_reflex
@requiere("fastapi")
@requiere_node
@requiere_playwright
def test_reflex_con_base_propia_y_con_api_en_el_navegador(proyecto, en_carpeta, monkeypatch):
    monkeypatch.setenv("VIRTUAL_ENV", str(Path(sys.executable).parent.parent))
    assert main(["nuevo", "crud", "producto", *CAMPOS, "--migrar"]) == 0
    assert (proyecto / "alembic").is_dir() and (proyecto / "datos.db").is_file()
    assert main(["nuevo", "crud-api", "articulo", *CAMPOS]) == 0
    with api_en_marcha("fastapi", en_carpeta, monkeypatch, [["articulo", *CAMPOS]]) as url_api:
        (proyecto / ".env").write_text(f"API_URL={url_api}\n", encoding="utf-8")
        frontend, backend = puerto_libre(), puerto_libre()
        entorno = {
            **os.environ,
            "REFLEX_FRONTEND_PORT": str(frontend),
            "REFLEX_BACKEND_PORT": str(backend),
            "REFLEX_API_URL": f"http://localhost:{backend}",
            "NO_PROXY": "127.0.0.1,localhost",
        }
        servidor = subprocess.Popen(
            [sys.executable, "-m", "reflex", "run"], cwd=proyecto, env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        try:
            _esperar(f"http://localhost:{frontend}/", servidor)
            for ruta in ("productos", "articulos"):
                resultado = ejecutar(["node", str(SCRIPT), f"http://localhost:{frontend}/{ruta}"], proyecto, env={"NO_PROXY": "127.0.0.1,localhost"})
                assert resultado.stdout.count("ok - ") == 8, (ruta, resultado.stdout)
        finally:
            servidor.terminate()
            try:
                servidor.wait(timeout=30)
            except subprocess.TimeoutExpired:
                servidor.kill()
