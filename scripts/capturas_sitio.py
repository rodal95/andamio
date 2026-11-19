"""Saca las capturas de pantalla de los proyectos generados funcionando (sitio/img/).

    python scripts/capturas_sitio.py

Genera con andamio un proyecto de Django, uno de React y uno de React Native, los
pone en marcha de verdad (API con datos, web compilada, app de Expo exportada para
web) y les saca fotos con Chromium (Playwright). Se ejecuta a mano cuando cambian
las plantillas, y las imágenes se suben al repositorio.

Necesita: las dependencias de Django instaladas en este Python
(pip install -r andamio/plantillas/django/_proyecto/requirements.txt), Node 22.13+
y Playwright para Node con Chromium.
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


def react(base: Path) -> None:
    print("React")
    andamio(base, "crear", "react", "mi-web")
    web = base / "mi-web"
    for argumentos in (["componente", "Tarjeta"], ["pagina", "Productos"], ["hook", "contador"], ["servicio", "producto", *CAMPOS]):
        andamio(web, "nuevo", *argumentos)
    ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], web)
    entorno = {"VITE_API_URL": "http://127.0.0.1:8000/api"}
    ejecutar([NPM, "run", "build"], web, entorno)
    with servir(web / "dist", 5173) as url:
        fotos([{"url": url, "archivo": str(IMAGENES / "react-inicio.jpg"), "ancho": 1000, "alto": 420}], base)
    shutil.copy(EJEMPLOS / "react-App.tsx", web / "src" / "App.tsx")
    shutil.copy(EJEMPLOS / "react-Tarjeta.module.css", web / "src" / "components" / "Tarjeta" / "Tarjeta.module.css")
    ejecutar([NPM, "run", "build"], web, entorno)
    with servir(web / "dist", 5173) as url:
        fotos([{"url": url, "archivo": str(IMAGENES / "react-final.jpg"), "ancho": 1000, "alto": 640, "esperar": "h3"}], base)


def react_native(base: Path) -> None:
    print("React Native")
    andamio(base, "crear", "react-native", "mi-app")
    app = base / "mi-app"
    for argumentos in (["pantalla", "detalle producto", "--carpeta", "productos"], ["componente", "Tarjeta"], ["hook", "contador"], ["servicio", "producto", *CAMPOS]):
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
    shutil.copy(EJEMPLOS / "react-native-index.tsx", app / "app" / "index.tsx")
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
            react(base)
            react_native(base)
        finally:
            servidor.terminate()
            servidor.wait(timeout=30)
    for imagen in sorted(IMAGENES.glob("*.jpg")):
        print(f"{imagen.relative_to(RAIZ)}  ({imagen.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    principal()
