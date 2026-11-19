"""Las combinaciones de las guías (sitio/ejemplos/) compilan de verdad.

Cada guía termina con recetas que combinan piezas: el código está en sitio/ejemplos/ y
la página lo muestra tal cual. Acá se arma el proyecto como dice la guía, se generan las
piezas de cada combinación, se copia su código y se compila (o se ejecuta) después de
cada una, porque cada combinación se arma sobre la anterior.
"""

import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from andamio.cli import main

from .node import NPM, NPX, ejecutar, npm_install, requiere_node
from .test_django import manage, requiere_django
from .test_reflex import requiere_reflex

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))
import sitio  # noqa: E402


def _armar(clave: str, variante: str, carpeta: Path, monkeypatch) -> Path:
    """Crea el proyecto con el nombre de la guía (las recetas lo usan: mi_app en Reflex)."""
    monkeypatch.chdir(carpeta)
    nombre = sitio.TECNOLOGIAS[clave]["carpeta"]
    assert main(["crear", clave, nombre, *(["--variante", variante] if variante else [])]) == 0
    return carpeta / nombre


def _aplicar(clave: str, variante: str, combinacion: dict, raiz: Path, monkeypatch) -> list[Path]:
    """Genera las piezas de la combinación y copia su código. Devuelve los archivos escritos."""
    monkeypatch.chdir(raiz)
    for lugar, comando in combinacion["pasos"]:
        # Los pasos con otro lugar ("En la app de React Native") se hacen en otro proyecto.
        if comando.startswith("nuevo ") and lugar in ("", "En este proyecto"):
            assert main(shlex.split(comando)) == 0, comando
    escritos = []
    for ruta, ejemplo in sitio.archivos_combinacion(combinacion, variante):
        destino = raiz / ruta
        assert destino.parent.is_dir(), f"{combinacion['id']}: {ruta} no está en una carpeta del proyecto"
        shutil.copy(ejemplo, destino)
        escritos.append(destino)
    return escritos


def test_python(en_carpeta, monkeypatch):
    raiz = _armar("python", "", en_carpeta, monkeypatch)
    for combinacion in sitio.COMBINACIONES["python"]:
        _aplicar("python", "", combinacion, raiz, monkeypatch)
    resultado = subprocess.run([sys.executable, "reporte.py"], cwd=raiz, capture_output=True, text=True, encoding="utf-8")
    assert resultado.returncode == 0, resultado.stderr
    assert "Yerba mate: $ 4850.5 (24 en stock)" in resultado.stdout and "Valor del stock: $ 116412.00" in resultado.stdout


@pytest.mark.lento
@requiere_node
@pytest.mark.parametrize("variante", ["ts", "js"])
@pytest.mark.parametrize("clave", ["react", "next", "next-fullstack"])
def test_web(clave, variante, en_carpeta, monkeypatch):
    raiz = _armar(clave, variante, en_carpeta, monkeypatch)
    npm_install(raiz)
    for combinacion in sitio.COMBINACIONES[clave]:
        _aplicar(clave, variante, combinacion, raiz, monkeypatch)
        # npm run build compila y revisa tipos (en el full stack, también las rutas de la API).
        ejecutar([NPM, "run", "build"], raiz, env={"NEXT_TELEMETRY_DISABLED": "1"})


@pytest.mark.lento
@requiere_node
@pytest.mark.parametrize("variante", ["ts", "js"])
def test_react_native(variante, en_carpeta, monkeypatch):
    raiz = _armar("react-native", variante, en_carpeta, monkeypatch)
    npm_install(raiz)
    for combinacion in sitio.COMBINACIONES["react-native"]:
        escritos = _aplicar("react-native", variante, combinacion, raiz, monkeypatch)
        if variante == "ts":
            ejecutar([NPX, "tsc", "--noEmit"], raiz)
        else:
            # En JavaScript no hay tipos: se controla que Babel (el de Expo) pueda leerlo.
            for archivo in escritos:
                codigo = (
                    "require('@babel/core').transformFileSync(process.argv[1], "
                    "{ presets: ['babel-preset-expo'], babelrc: false, configFile: false })"
                )
                ejecutar(["node", "-e", codigo, str(archivo)], raiz)


@pytest.mark.lento
@requiere_reflex
def test_reflex(en_carpeta, monkeypatch):
    raiz = _armar("reflex", "", en_carpeta, monkeypatch)
    for combinacion in sitio.COMBINACIONES["reflex"]:
        _aplicar("reflex", "", combinacion, raiz, monkeypatch)
        # compile arma todas las páginas: un error en los componentes o en el estado aparece acá.
        ejecutar([sys.executable, "-m", "reflex", "compile"], raiz, timeout=900)


@pytest.mark.skipif(shutil.which("node") is None, reason="no hay Node para revisar la sintaxis de JavaScript")
def test_web_html(en_carpeta, monkeypatch):
    """La web HTML no compila: se controla la sintaxis de cada .js y que cada import exista."""
    raiz = _armar("web", "", en_carpeta, monkeypatch)
    for combinacion in sitio.COMBINACIONES["web"]:
        for archivo in _aplicar("web", "", combinacion, raiz, monkeypatch):
            if archivo.suffix != ".js":
                continue
            codigo = archivo.read_text(encoding="utf-8")
            resultado = subprocess.run(["node", "--input-type=module", "--check"], input=codigo, capture_output=True, text=True)
            assert resultado.returncode == 0, f"{archivo}\n{resultado.stderr}"
            for importado in re.findall(r"from '(\.[^']+)'", codigo):
                assert (archivo.parent / importado).resolve().is_file(), f"{archivo.name} importa {importado}, que no existe"


@pytest.mark.lento
@requiere_node
def test_vue(en_carpeta, monkeypatch):
    raiz = _armar("vue", "", en_carpeta, monkeypatch)
    npm_install(raiz)
    for combinacion in sitio.COMBINACIONES["vue"]:
        _aplicar("vue", "", combinacion, raiz, monkeypatch)
        # vite build compila cada .vue que usa el router (la página del catálogo incluida).
        ejecutar([NPM, "run", "build"], raiz)


@requiere_django
def test_django_web(en_carpeta, monkeypatch):
    raiz = _armar("django-web", "", en_carpeta, monkeypatch)
    for combinacion in sitio.COMBINACIONES["django-web"]:
        _aplicar("django-web", "", combinacion, raiz, monkeypatch)
        for argumentos in (["check"], ["makemigrations"], ["test"]):
            resultado = manage(raiz, *argumentos)
            assert resultado.returncode == 0, f"{combinacion['id']}: manage.py {' '.join(argumentos)}\n{resultado.stdout}\n{resultado.stderr}"
    # El catálogo muestra solo lo que tiene stock, ordenado por precio.
    codigo = (
        "import django, os\n"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')\n"
        "django.setup()\n"
        "from django.test.utils import setup_test_environment\n"
        "from django.test.runner import DiscoverRunner\n"
        "setup_test_environment(); DiscoverRunner(verbosity=0).setup_databases()\n"
        "from django.test import Client\n"
        "from productos.models import Producto\n"
        "Producto.objects.create(nombre='Mate', precio=4200, stock=3)\n"
        "Producto.objects.create(nombre='Yerba', precio=1500, stock=10)\n"
        "Producto.objects.create(nombre='Bombilla', precio=900, stock=0)\n"
        "html = Client().get('/catalogo/').content.decode()\n"
        "assert html.index('Yerba') < html.index('Mate') and 'Bombilla' not in html, html\n"
        "print('ok')\n"
    )
    resultado = subprocess.run([sys.executable, "-c", codigo], cwd=raiz, capture_output=True, text=True, encoding="utf-8")
    assert resultado.returncode == 0 and "ok" in resultado.stdout, resultado.stderr
