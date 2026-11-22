"""Stacks next (frontend que usa una API) y next-fullstack (con su API y su base de datos)."""

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from andamio import stacks
from andamio.cli import main
from andamio.nucleo.deteccion import buscar_proyecto

from .apis import NODE, api_en_marcha, puerto_libre, requiere
from .node import NPM, NPX, ejecutar, npm_install, requiere_node
from .test_coherencia import CAMPOS
from .test_crud_navegador import SCRIPT as SCRIPT_NAVEGADOR
from .test_crud_navegador import requiere_playwright

EXT = {"ts": ("ts", "tsx"), "js": ("js", "jsx")}


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def _archivos(raiz):
    return {p.relative_to(raiz).as_posix() for p in raiz.rglob("*") if p.is_file()}


@pytest.fixture(params=["ts", "js"])
def variante(request):
    return request.param


@pytest.fixture
def web(en_carpeta, monkeypatch, variante):
    assert main(["crear", "next", "Mi Web", "--variante", variante]) == 0
    monkeypatch.chdir(en_carpeta / "mi-web")
    return en_carpeta / "mi-web"


@pytest.fixture
def app(en_carpeta, monkeypatch, variante):
    assert main(["crear", "next-fullstack", "Mi App", "--variante", variante]) == 0
    monkeypatch.chdir(en_carpeta / "mi-app")
    return en_carpeta / "mi-app"


# --- Estructura ----------------------------------------------------------------------


def test_proyecto_frontend(web, variante):
    ext, extx = EXT[variante]
    esperados = {
        ".env",
        ".env.example",
        ".gitignore",
        "andamio-guia.html",
        "README.md",
        "package.json",
        "jsconfig.json" if variante == "js" else "tsconfig.json",
        "next.config.ts" if variante == "ts" else "next.config.mjs",
        f"app/layout.{extx}",
        f"app/page.{extx}",
        "app/globals.css",
        f"components/index.{ext}",
        *(f"components/{c}/{c}.{extx}" for c in ("Navbar", "Footer", "Layout")),
        *(f"components/{c}/{c}.module.css" for c in ("Navbar", "Footer", "Layout")),
        *(f"components/{c}/index.{ext}" for c in ("Navbar", "Footer", "Layout")),
        "hooks/.gitkeep",
        "services/.gitkeep",
        "public/.gitkeep",
    }
    assert _archivos(web) == esperados
    paquete = json.loads(leer(web / "package.json"))
    assert paquete["name"] == "mi-web" and "next" in paquete["dependencies"]
    assert "prisma" not in json.dumps(paquete)
    assert ("typescript" in paquete.get("devDependencies", {})) == (variante == "ts")
    assert "NEXT_PUBLIC_API_URL=http://localhost:8000/api" in leer(web / ".env")
    assert ".env.example" not in leer(web / ".gitignore")  # .env.example se sube a git
    assert "next/font/google" not in leer(web / f"app/layout.{extx}")  # no descarga fuentes al compilar
    # El menú y el pie son componentes; app/layout los muestra con el Layout.
    assert "<Layout>{children}</Layout>" in leer(web / f"app/layout.{extx}")
    assert "andamio:enlaces" in leer(web / f"components/Navbar/Navbar.{extx}")
    assert "<Navbar />" in leer(web / f"components/Layout/Layout.{extx}")
    for archivo in web.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo), archivo


def test_enlaces_en_un_proyecto_sin_navbar(web, variante):
    """Un proyecto de una versión anterior (el menú en app/layout): los enlaces van ahí."""
    _, extx = EXT[variante]
    layout = web / f"app/layout.{extx}"
    layout.write_text(
        "import Link from 'next/link';\n\nexport default function RootLayout({ children }) {\n  return (\n    <html>\n      <body>\n"
        "        <nav>\n          <Link href=\"/\">Inicio</Link>\n          {/* --- andamio:enlaces (no borrar esta línea) --- */}\n"
        "        </nav>\n        {children}\n      </body>\n    </html>\n  );\n}\n",
        encoding="utf-8",
    )
    for carpeta in ("Navbar", "Footer", "Layout"):
        for archivo in (web / "components" / carpeta).iterdir():
            archivo.unlink()
        (web / "components" / carpeta).rmdir()
    assert main(["nuevo", "pagina", "Contacto"]) == 0
    assert '<Link href="/contacto">Contacto</Link>\n          {/* --- andamio:enlaces' in leer(layout)


def test_proyecto_fullstack_extiende_al_frontend(app, variante):
    ext, extx = EXT[variante]
    archivos = _archivos(app)
    # Lo del frontend...
    for comun in (f"app/layout.{extx}", f"app/page.{extx}", "app/globals.css", f"components/index.{ext}"):
        assert comun in archivos, comun
    # ...más la API y la base de datos.
    for propio in (
        "prisma/schema.prisma",
        f"prisma.config.{ext}",
        f"proxy.{ext}",
        f"tests/api.{ext}",
        *(f"lib/{n}.{ext}" for n in ("db", "errores", "fechas", "validacion")),
    ):
        assert propio in archivos, propio
    paquete = json.loads(leer(app / "package.json"))
    assert paquete["type"] == "module"
    assert "@prisma/client" in paquete["dependencies"]
    assert "prisma generate" in paquete["scripts"]["postinstall"]
    assert "--force-reset" not in paquete["scripts"]["pretest"]
    assert "trailingSlash: true" in leer(app / ("next.config.ts" if variante == "ts" else "next.config.mjs"))
    assert "generated/" in leer(app / ".gitignore") and "datos.db" in leer(app / ".gitignore")
    for archivo in app.rglob("*"):
        if archivo.is_file():
            assert "@@" not in leer(archivo).replace("@@map", ""), archivo


# --- Piezas de interfaz (las mismas en los dos) -----------------------------------------


@pytest.mark.parametrize("stack", ["next", "next-fullstack"])
def test_piezas_de_interfaz(stack, variante, en_carpeta, monkeypatch):
    ext, extx = EXT[variante]
    assert main(["crear", stack, "proyecto", "--variante", variante]) == 0
    raiz = en_carpeta / "proyecto"
    monkeypatch.chdir(raiz)
    for argumentos in (["componente", "Tarjeta"], ["pagina", "Contacto"], ["hook", "contador"], ["crud", "producto", *CAMPOS]):
        assert main(["nuevo", *argumentos]) == 0, argumentos
    assert (raiz / f"components/Tarjeta/Tarjeta.{extx}").is_file()
    assert (raiz / f"hooks/useContador.{ext}").is_file()
    assert (raiz / f"app/contacto/page.{extx}").is_file()
    for ruta in ("page", "nuevo/page", "[id]/page", "[id]/editar/page", "ProductoFormulario"):
        assert (raiz / f"app/productos/{ruta}.{extx}").is_file(), ruta
    navbar = leer(raiz / f"components/Navbar/Navbar.{extx}")
    assert '<Link href="/contacto">Contacto</Link>\n      <Link href="/productos">Productos</Link>' in navbar
    indice = leer(raiz / f"components/index.{ext}")
    assert "export { Tarjeta } from './Tarjeta';" in indice and "export { ProductoDetalle } from './ProductoDetalle';" in indice
    lista = leer(raiz / f"app/productos/page.{extx}")
    assert lista.startswith("'use client';") and "export default function ProductosPage()" in lista
    assert "from 'next/navigation'" in leer(raiz / f"app/productos/ProductoFormulario.{extx}")
    http = leer(raiz / f"services/http.{ext}")
    por_defecto = "'/api'" if stack == "next-fullstack" else "'http://localhost:8000/api'"
    assert f"process.env.NEXT_PUBLIC_API_URL ?? {por_defecto}" in http


@pytest.mark.parametrize("argumentos, esperado", [(["pagina", "Api"], "app/api"), (["crud", "api", "nombre", "--plural", "api"], "app/api")])
def test_rutas_reservadas(web, capsys, argumentos, esperado):
    capsys.readouterr()
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_el_frontend_no_tiene_recurso(web, capsys):
    # La API va en otro proyecto (Django, FastAPI o Express) o en uno full stack.
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 1
    assert "recurso" in capsys.readouterr().err


# --- Recurso (full stack) ---------------------------------------------------------------


def test_recurso_fullstack(app, variante):
    ext = EXT[variante][0]
    assert main(["nuevo", "recurso", "producto", *CAMPOS]) == 0
    for archivo in (f"app/api/productos/route.{ext}", f"app/api/productos/[id]/route.{ext}", f"app/api/productos/esquema.{ext}", f"tests/productos.test.{ext}"):
        assert (app / archivo).is_file(), archivo
    assert "model Producto {" in leer(app / "prisma/schema.prisma")
    lista = leer(app / f"app/api/productos/route.{ext}")
    assert "export async function GET(request" in lista and "export async function POST(request" in lista
    detalle = leer(app / f"app/api/productos/[id]/route.{ext}")
    parametros = "request: Request, contexto: Contexto" if variante == "ts" else "request, contexto"
    for metodo in ("GET", "PUT", "PATCH", "DELETE"):
        assert f"export async function {metodo}({parametros})" in detalle, metodo
    esquema = leer(app / f"app/api/productos/esquema.{ext}")
    assert "from '@/lib/validacion'" in esquema and "publicado: fechaHora()," in esquema
    if variante == "js":
        assert "import type" not in lista + detalle + esquema


def test_recurso_y_crud_se_sugieren_mutuamente(app, capsys):
    capsys.readouterr()
    assert main(["nuevo", "crud", "producto", "nombre", "precio:decimal"]) == 0
    salida = capsys.readouterr().out
    assert "python -m andamio nuevo recurso producto nombre:str precio:decimal --migrar" in salida
    assert main(["nuevo", "recurso", "cliente", "nombre"]) == 0
    assert main(["nuevo", "crud", "cliente", "nombre"]) == 0
    assert "nuevo recurso cliente" not in capsys.readouterr().out  # ya existe: no lo sugiere


@pytest.mark.parametrize(
    "argumentos, esperado",
    [
        (["recurso", "generado", "nombre", "--plural", "generated"], "cliente de Prisma"),
        (["recurso", "producto", "search"], "?search="),
        (["recurso", "productos", "nombre"], "parece estar en plural"),
    ],
)
def test_recurso_nombres_no_permitidos(app, capsys, argumentos, esperado):
    capsys.readouterr()
    assert main(["nuevo", *argumentos]) == 1
    assert esperado in capsys.readouterr().err


def test_recurso_repetido_no_toca_nada(app, capsys):
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 0
    antes = {p: p.read_bytes() for p in app.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert main(["nuevo", "recurso", "producto", "nombre"]) == 1
    assert antes == {p: p.read_bytes() for p in app.rglob("*") if p.is_file()}


def test_exportar_piezas_heredadas(app):
    # crud vive en las plantillas de next: next-fullstack las exporta igual.
    assert main(["plantillas", "exportar", "crud"]) == 0
    assert list((app / ".andamio/plantillas/next-fullstack/crud").rglob("page.*"))


# --- Detección y menú ----------------------------------------------------------------------


def test_deteccion(en_carpeta):
    assert main(["crear", "next", "mi-web"]) == 0
    assert main(["crear", "next-fullstack", "mi-app"]) == 0
    web, app = en_carpeta / "mi-web", en_carpeta / "mi-app"
    next_, fullstack = stacks.por_clave("next"), stacks.por_clave("next-fullstack")
    assert buscar_proyecto(web / "app") == (next_, web)
    assert buscar_proyecto(app / "app") == (fullstack, app)
    assert buscar_proyecto(app / "prisma") == (fullstack, app)


def test_menu(en_carpeta, respuestas):
    respuestas(["10", "1", "mi app", "s"])  # 10: full stack, 1: TypeScript
    assert main([]) == 0
    assert (en_carpeta / "mi-app/proxy.ts").is_file()
    respuestas(["9", "2", "mi web", "s"])  # 9: frontend, 2: JavaScript
    assert main([]) == 0
    assert (en_carpeta / "mi-web/app/layout.jsx").is_file()


# --- Con Node: instalar, compilar y usar en el navegador ----------------------------------


def _esperar(url: str, proceso: subprocess.Popen) -> None:
    for _ in range(120):
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except urllib.error.HTTPError:
            return
        except OSError:
            if proceso.poll() is not None:
                pytest.fail("Next.js terminó al arrancar")
            time.sleep(0.5)
    pytest.fail(f"No respondió {url}")


def _compilar_y_probar(raiz: Path, puerto: int, entorno: dict | None = None) -> None:
    """next build, next start y el CRUD en Chromium (el mismo script que para React)."""
    ejecutar([NPM, "run", "build"], raiz, env=entorno)
    servidor = subprocess.Popen(
        [NODE, "node_modules/next/dist/bin/next", "start", "-p", str(puerto), "-H", "127.0.0.1"],
        cwd=raiz,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        url = f"http://127.0.0.1:{puerto}"
        _esperar(url, servidor)
        resultado = ejecutar(["node", str(SCRIPT_NAVEGADOR), url], raiz, env={"NO_PROXY": "127.0.0.1,localhost"})
        assert resultado.stdout.count("ok - ") == 10, resultado.stdout
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


@pytest.mark.lento
@requiere_node
@requiere_playwright
def test_fullstack_instala_migra_pasa_tests_y_funciona_en_el_navegador(app, variante):
    npm_install(app)
    if variante == "js":
        assert main(["nuevo", "recurso", "producto", *CAMPOS, "--migrar"]) == 0
    else:
        assert main(["nuevo", "recurso", "producto", *CAMPOS]) == 0
        ejecutar([NPX, "prisma", "migrate", "dev", "--name", "productos"], app)
    assert main(["nuevo", "crud", "producto", *CAMPOS]) == 0
    resultado = ejecutar([NPM, "test"], app)
    assert "# pass 5" in resultado.stdout and "# fail 0" in resultado.stdout, resultado.stdout[-3000:]
    _compilar_y_probar(app, puerto_libre())


@pytest.mark.lento
@requiere_node
@requiere_playwright
@requiere("fastapi")
def test_frontend_compila_y_usa_la_api_en_el_navegador(web, variante, en_carpeta, monkeypatch):
    for argumentos in (["componente", "Tarjeta"], ["pagina", "Contacto"], ["hook", "contador"], ["servicio", "cliente", "nombre"], ["crud", "producto", *CAMPOS]):
        assert main(["nuevo", *argumentos]) == 0
    npm_install(web)
    puerto = puerto_libre()
    # La API tiene que aceptar pedidos de la web (CORS), que va a estar en ese puerto.
    with api_en_marcha("fastapi", en_carpeta, monkeypatch, [["producto", *CAMPOS]], cors=f"http://127.0.0.1:{puerto}") as url_api:
        # La dirección de la API queda dentro de la web al compilar (NEXT_PUBLIC_...).
        _compilar_y_probar(web, puerto, {"NEXT_PUBLIC_API_URL": url_api})

