"""Saca las capturas de pantalla de los proyectos generados funcionando (sitio/img/).

    python scripts/capturas_sitio.py

Genera con andamio un proyecto de cada tecnología (Django, FastAPI, Express, React,
React Native, Next.js en sus dos formas y Reflex), los pone en marcha de verdad (APIs con
datos, webs compiladas, app de Expo exportada para web) y les saca fotos con Chromium
(Playwright). Se ejecuta a mano cuando cambian las plantillas, y las imágenes se
suben al repositorio.

Necesita: las dependencias de Django y de FastAPI instaladas en este Python
(pip install -r andamio/plantillas/django/_proyecto/requirements.txt y lo mismo con
andamio/plantillas/fastapi/_proyecto/requirements.txt), Node 22.13+ y Playwright
para Node con Chromium.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from andamio.cli import main  # noqa: E402

IMAGENES = RAIZ / "sitio" / "img"
EJEMPLOS = RAIZ / "sitio" / "ejemplos"
CAMPOS = ["nombre:str", "precio:decimal", "stock:int"]
PRODUCTOS = [("Yerba mate 1 kg", "4850.00", 24), ("Mate de calabaza", "12500.00", 6), ("Bombilla de alpaca", "9300.50", 11)]
NPM = shutil.which("npm") or "npm"
NPX = shutil.which("npx") or "npx"


def andamio(carpeta: Path, *argumentos: str) -> None:
    anterior = os.getcwd()
    os.chdir(carpeta)
    try:
        with contextlib.redirect_stdout(open(os.devnull, "w", encoding="utf-8")):
            codigo = main(list(argumentos))
    finally:
        os.chdir(anterior)
    if codigo != 0:
        raise SystemExit(f"andamio {' '.join(argumentos)} falló")


def ejecutar(comando: list[str], cwd: Path, env: dict | None = None) -> None:
    print("   $", " ".join(comando))
    resultado = subprocess.run(comando, cwd=cwd, env={**os.environ, "CI": "1", **(env or {})}, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise SystemExit(f"Falló: {' '.join(comando)}\n{resultado.stdout[-2000:]}\n{resultado.stderr[-2000:]}")


def esperar_url(url: str, segundos: int = 60) -> None:
    for _ in range(segundos * 2):
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"No respondió {url}")


class _SPA(http.server.SimpleHTTPRequestHandler):
    """Servidor de archivos que, si la ruta no existe, devuelve index.html (apps de una página)."""

    def send_head(self):  # noqa: N802
        ruta = Path(self.translate_path(self.path))
        if not ruta.exists() and not Path(str(ruta) + ".html").exists():
            self.path = "/index.html"
        elif not ruta.exists():
            self.path += ".html"
        return super().send_head()

    def log_message(self, *args):  # silencio
        pass


@contextlib.contextmanager
def servir(carpeta: Path, puerto: int, host: str = "127.0.0.1"):
    servidor = http.server.ThreadingHTTPServer((host, puerto), functools.partial(_SPA, directory=str(carpeta)))
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    try:
        yield f"http://{host}:{puerto}"
    finally:
        servidor.shutdown()


NODE_CAPTURAS = r"""
const { chromium } = require('playwright');
const tareas = JSON.parse(process.argv[2]);
(async () => {
  const navegador = await chromium.launch();
  for (const t of tareas) {
    const ctx = await navegador.newContext({
      viewport: { width: t.ancho, height: t.alto }, deviceScaleFactor: 2,
      isMobile: !!t.telefono, hasTouch: !!t.telefono, locale: 'es-AR', colorScheme: 'light',
    });
    const pagina = await ctx.newPage();
    if (t.login) {
      await pagina.goto(t.login.url);
      await pagina.fill('#id_username', t.login.usuario);
      await pagina.fill('#id_password', t.login.clave);
      await pagina.click('input[type=submit]');
      await pagina.waitForLoadState('networkidle');
    }
    await pagina.goto(t.url, { waitUntil: 'networkidle' });
    if (t.esperar) await pagina.waitForSelector(t.esperar, { timeout: 30000 });
    for (const selector of t.clics || []) await pagina.locator(selector).first().click();
    for (const [etiqueta, valor] of Object.entries(t.llenar || {})) await pagina.getByLabel(etiqueta).fill(valor);
    if (t.enviar) await pagina.getByRole('button', { name: t.enviar }).click();
    if (t.esperar_despues) await pagina.waitForSelector(t.esperar_despues, { timeout: 30000 });
    if (t.mostrar) await pagina.locator(t.mostrar).first().evaluate((el) => el.scrollIntoView({ block: 'start' }));
    await pagina.waitForTimeout(800);
    await pagina.screenshot({ path: t.archivo, type: 'jpeg', quality: 88 });
    console.log('  foto:', t.archivo);
    await ctx.close();
  }
  await navegador.close();
})().catch((e) => { console.error(e); process.exit(1); });
"""


def fotos(tareas: list[dict], carpeta: Path) -> None:
    script = carpeta / "capturas.js"
    script.write_text(NODE_CAPTURAS, encoding="utf-8")
    resultado = subprocess.run(["node", str(script), json.dumps(tareas)], cwd=carpeta, text=True)
    if resultado.returncode != 0:
        raise SystemExit("Fallaron las capturas")


def django(base: Path) -> subprocess.Popen:
    print("Django")
    andamio(base, "crear", "django", "mi-api")
    api = base / "mi-api"
    andamio(api, "nuevo", "recurso", "producto", *CAMPOS)
    ejecutar([sys.executable, "manage.py", "makemigrations", "productos"], api)
    ejecutar([sys.executable, "manage.py", "migrate"], api)
    alta = "from productos.models import Producto\n" + "\n".join(
        f"Producto.objects.create(nombre={n!r}, precio={p!r}, stock={s})" for n, p, s in PRODUCTOS
    )
    ejecutar([sys.executable, "manage.py", "shell", "-c", alta], api)
    ejecutar(
        [sys.executable, "manage.py", "createsuperuser", "--noinput"],
        api,
        env={"DJANGO_SUPERUSER_USERNAME": "docente", "DJANGO_SUPERUSER_PASSWORD": "clave-de-prueba-123", "DJANGO_SUPERUSER_EMAIL": "docente@ejemplo.com"},
    )
    servidor = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        cwd=api,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    esperar_url("http://127.0.0.1:8000/api/productos/")
    fotos(
        [
            {"url": "http://127.0.0.1:8000/api/docs/", "archivo": str(IMAGENES / "django-swagger.jpg"), "ancho": 1200, "alto": 760, "esperar": ".opblock"},
            {"url": "http://127.0.0.1:8000/api/productos/", "archivo": str(IMAGENES / "django-api.jpg"), "ancho": 1200, "alto": 760},
            {
                "url": "http://127.0.0.1:8000/admin/productos/producto/",
                "archivo": str(IMAGENES / "django-admin.jpg"),
                "ancho": 1200,
                "alto": 560,
                "login": {"url": "http://127.0.0.1:8000/admin/login/", "usuario": "docente", "clave": "clave-de-prueba-123"},
            },
        ],
        base,
    )
    return servidor


def fastapi(base: Path) -> None:
    print("FastAPI")
    carpeta = base / "fastapi"
    carpeta.mkdir()
    andamio(carpeta, "crear", "fastapi", "mi-api")
    api = carpeta / "mi-api"
    andamio(api, "nuevo", "recurso", "producto", *CAMPOS)
    # En el puerto 8001: el 8000 lo usa Django, que necesitan las capturas de React.
    servidor = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=api,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        esperar_url("http://127.0.0.1:8001/api/productos/")
        _cargar_productos("http://127.0.0.1:8001/api/productos/")
        _fotos_swagger(8001, "fastapi", base)
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


def _cargar_productos(url: str) -> None:
    for nombre, precio, stock in PRODUCTOS:
        datos = json.dumps({"nombre": nombre, "precio": precio, "stock": stock}).encode()
        pedido = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(pedido, timeout=10)


def _fotos_swagger(puerto: int, nombre: str, base: Path) -> None:
    """La documentación, y GET /api/productos/ ejecutado desde Swagger (Try it out → Execute)."""
    fotos(
        [
            {"url": f"http://127.0.0.1:{puerto}/docs", "archivo": str(IMAGENES / f"{nombre}-swagger.jpg"), "ancho": 1200, "alto": 760, "esperar": ".opblock"},
            {
                "url": f"http://127.0.0.1:{puerto}/docs",
                "archivo": str(IMAGENES / f"{nombre}-api.jpg"),
                "ancho": 1200,
                "alto": 760,
                "esperar": ".opblock",
                "clics": [".opblock-get .opblock-summary", "button.try-out__btn", "button.execute"],
                "esperar_despues": ".live-responses-table .highlight-code",
                "mostrar": ".live-responses-table",
            },
        ],
        base,
    )


def express(base: Path) -> None:
    print("Express")
    carpeta = base / "express"
    carpeta.mkdir()
    andamio(carpeta, "crear", "express", "mi-api")
    api = carpeta / "mi-api"
    andamio(api, "nuevo", "recurso", "producto", *CAMPOS)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], api)
    ejecutar([NPX, "prisma", "migrate", "dev", "--name", "productos"], api)
    # En el puerto 8002: el 8000 lo usa Django y el 8001 FastAPI.
    servidor = subprocess.Popen(
        ["node", "--import", "tsx", "src/servidor.ts"],
        cwd=api,
        env={**os.environ, "PORT": "8002"},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        esperar_url("http://127.0.0.1:8002/api/productos/")
        _cargar_productos("http://127.0.0.1:8002/api/productos/")
        _fotos_swagger(8002, "express", base)
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


def react(base: Path) -> None:
    print("React")
    andamio(base, "crear", "react", "mi-web")
    web = base / "mi-web"
    for argumentos in (["componente", "Tarjeta"], ["pagina", "Contacto"], ["hook", "contador"], ["crud", "producto", *CAMPOS]):
        andamio(web, "nuevo", *argumentos)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], web)
    ejecutar([NPM, "run", "build"], web, {"VITE_API_URL": "http://127.0.0.1:8000/api"})
    with servir(web / "dist", 5173) as url:
        fotos(
            [
                {"url": url, "archivo": str(IMAGENES / "react-inicio.jpg"), "ancho": 1000, "alto": 420},
                {"url": f"{url}/productos", "archivo": str(IMAGENES / "react-crud-lista.jpg"), "ancho": 1000, "alto": 480, "esperar": "text=Mate de calabaza"},
                {"url": f"{url}/productos/1", "archivo": str(IMAGENES / "react-crud-detalle.jpg"), "ancho": 1000, "alto": 520, "esperar": "dd"},
                {
                    "url": f"{url}/productos/nuevo",
                    "archivo": str(IMAGENES / "react-crud-formulario.jpg"),
                    "ancho": 1000,
                    "alto": 640,
                    "llenar": {"Nombre": "Termo de acero", "Precio": "123456789012", "Stock": "3"},
                    "enviar": "Guardar",
                    "esperar_despues": "small",
                },
            ],
            base,
        )


@contextlib.contextmanager
def next_en_marcha(carpeta: Path, puerto: int):
    """next start en un solo proceso (así terminate() lo cierra)."""
    servidor = subprocess.Popen(
        ["node", "node_modules/next/dist/bin/next", "start", "-p", str(puerto)],
        cwd=carpeta,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        esperar_url(f"http://localhost:{puerto}/")
        yield f"http://localhost:{puerto}"
    finally:
        servidor.terminate()
        servidor.wait(timeout=30)


def next_frontend(base: Path) -> None:
    """La web de Next.js usando la API de Django (que ya está andando en el 8000)."""
    print("Next.js (frontend)")
    carpeta = base / "next"
    carpeta.mkdir()
    andamio(carpeta, "crear", "next", "mi-web")
    web = carpeta / "mi-web"
    for argumentos in (["pagina", "Contacto"], ["crud", "producto", *CAMPOS]):
        andamio(web, "nuevo", *argumentos)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], web)
    ejecutar([NPM, "run", "build"], web, {"NEXT_PUBLIC_API_URL": "http://127.0.0.1:8000/api"})
    with next_en_marcha(web, 3000) as url:
        fotos(
            [
                {"url": url, "archivo": str(IMAGENES / "next-inicio.jpg"), "ancho": 1000, "alto": 420},
                {"url": f"{url}/productos", "archivo": str(IMAGENES / "next-crud-lista.jpg"), "ancho": 1000, "alto": 480, "esperar": "text=Mate de calabaza"},
            ],
            base,
        )


def next_fullstack(base: Path) -> None:
    """La aplicación full stack: sus páginas usan su propia API y su base de datos."""
    print("Next.js full stack")
    carpeta = base / "next-fullstack"
    carpeta.mkdir()
    andamio(carpeta, "crear", "next-fullstack", "mi-app")
    app = carpeta / "mi-app"
    for argumentos in (["recurso", "producto", *CAMPOS], ["crud", "producto", *CAMPOS]):
        andamio(app, "nuevo", *argumentos)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], app)
    ejecutar([NPX, "prisma", "migrate", "dev", "--name", "productos"], app)
    ejecutar([NPM, "run", "build"], app)
    with next_en_marcha(app, 3001) as url:
        _cargar_productos(f"{url}/api/productos/")
        fotos(
            [
                {"url": f"{url}/productos/2/", "archivo": str(IMAGENES / "next-fullstack-crud-detalle.jpg"), "ancho": 1000, "alto": 520, "esperar": "dd"},
                {
                    "url": f"{url}/productos/nuevo/",
                    "archivo": str(IMAGENES / "next-fullstack-crud-formulario.jpg"),
                    "ancho": 1000,
                    "alto": 640,
                    "llenar": {"Nombre": "Termo de acero", "Precio": "123456789012", "Stock": "3"},
                    "enviar": "Guardar",
                    "esperar_despues": "small",
                },
            ],
            base,
        )


def reflex(base: Path) -> None:
    """La página del crud de Reflex, con datos y un error de validación en el formulario."""
    print("Reflex")
    carpeta = base / "reflex"
    carpeta.mkdir()
    andamio(carpeta, "crear", "reflex", "mi-app")
    app = carpeta / "mi-app"
    os.environ["VIRTUAL_ENV"] = str(Path(sys.executable).parent.parent)  # --migrar usa este Python
    andamio(app, "nuevo", "crud", "producto", *CAMPOS, "--migrar")
    alta = (
        "import reflex as rx\nfrom mi_app.modelos.producto import Producto\nwith rx.session() as s:\n"
        + "".join(f"    s.add(Producto(nombre={n!r}, precio={p!r}, stock={st}))\n" for n, p, st in PRODUCTOS)
        + "    s.commit()\n"
    )
    ejecutar([sys.executable, "-c", alta], app)
    entorno = {**os.environ, "REFLEX_FRONTEND_PORT": "3005", "REFLEX_BACKEND_PORT": "8005", "REFLEX_API_URL": "http://localhost:8005"}
    servidor = subprocess.Popen(
        [sys.executable, "-m", "reflex", "run"], cwd=app, env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        esperar_url("http://localhost:3005/", 600)
        fotos(
            [
                {
                    "url": "http://localhost:3005/productos",
                    "archivo": str(IMAGENES / "reflex-crud.jpg"),
                    "ancho": 1000,
                    "alto": 760,
                    "esperar": "text=Mate de calabaza",
                    "llenar": {"Nombre": "Termo de acero", "Precio": "123456789012", "Stock": "3"},
                    "enviar": "Guardar",
                    "esperar_despues": "text=dígitos",
                },
            ],
            base,
        )
    finally:
        servidor.terminate()
        servidor.wait(timeout=60)


def react_native(base: Path) -> None:
    print("React Native")
    andamio(base, "crear", "react-native", "mi-app")
    app = base / "mi-app"
    for argumentos in (
        ["pantalla", "detalle producto", "--carpeta", "productos"],
        ["componente", "Tarjeta"],
        ["hook", "contador"],
        ["hook", "productos"],
        ["servicio", "producto", *CAMPOS],
    ):
        andamio(app, "nuevo", *argumentos)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], app)
    entorno = {"EXPO_PUBLIC_API_URL": "http://localhost:8000/api", "EXPO_OFFLINE": "1"}
    telefono = {"ancho": 390, "alto": 760, "telefono": True}
    ejecutar([NPX, "expo", "export", "--platform", "web", "--output-dir", "web"], app, entorno)
    with servir(app / "web", 8081, "localhost") as url:
        fotos(
            [
                {"url": url, "archivo": str(IMAGENES / "react-native-inicio.jpg"), **telefono},
                {"url": f"{url}/productos/detalle-producto", "archivo": str(IMAGENES / "react-native-detalle.jpg"), **telefono},
            ],
            base,
        )
    # El código de la última combinación de la guía (sitio/ejemplos/react-native/ts/).
    for ejemplo, destino in (
        ("3-useProductos.ts", "hooks/useProductos.ts"),
        ("4-index.tsx", "app/index.tsx"),
        ("4-detalle-producto.tsx", "app/productos/detalle-producto.tsx"),
    ):
        shutil.copy(EJEMPLOS / "react-native" / "ts" / ejemplo, app / destino)
    shutil.rmtree(app / "web")
    ejecutar([NPX, "expo", "export", "--platform", "web", "--output-dir", "web"], app, entorno)
    with servir(app / "web", 8081, "localhost") as url:
        fotos([{"url": url, "archivo": str(IMAGENES / "react-native-final.jpg"), "esperar": "text=Yerba mate 1 kg", **telefono}], base)


def principal() -> None:
    IMAGENES.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporal:
        base = Path(temporal)
        servidor = django(base)
        try:
            fastapi(base)
            express(base)
            react(base)
            next_frontend(base)
            next_fullstack(base)
            reflex(base)
            react_native(base)
        finally:
            servidor.terminate()
            servidor.wait(timeout=30)
    for imagen in sorted(IMAGENES.glob("*.jpg")):
        print(f"{imagen.relative_to(RAIZ)}  ({imagen.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    principal()
