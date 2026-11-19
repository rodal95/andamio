"""Genera sitio/datos.js con demostraciones reales de andamio para la página web.

    python scripts/sitio.py

Ejecuta andamio de verdad (crear proyectos, generar piezas, una sesión del menú)
y guarda lo que muestra la terminal y los archivos que genera. Así la página
nunca muestra algo distinto de lo que hace la herramienta. El workflow del sitio
lo ejecuta antes de publicar.
"""

from __future__ import annotations

import builtins
import contextlib
import io
import json
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import andamio  # noqa: E402
from andamio.cli import main  # noqa: E402
from andamio.nucleo import consola  # noqa: E402

DESTINO = RAIZ / "sitio" / "datos.js"

# (clave, título, carpeta, [comandos después de "crear"], archivo que se muestra primero)
DEMOS = [
    (
        "python",
        "Python + SQLite",
        "mi-tienda",
        ["nuevo entidad producto nombre:str precio:float stock:int"],
        "entidades/producto.py",
    ),
    (
        "django",
        "Django REST",
        "mi-api",
        ["nuevo recurso producto nombre:str precio:decimal stock:int"],
        "productos/views.py",
    ),
    (
        "react",
        "React + Vite",
        "mi-web",
        ["nuevo componente Tarjeta", "nuevo servicio producto nombre:str precio:decimal stock:int"],
        "src/services/productoService.ts",
    ),
    (
        "react-native",
        "React Native + Expo",
        "mi-app",
        ['nuevo pantalla "detalle producto" --carpeta productos', "nuevo servicio producto nombre:str precio:decimal stock:int"],
        "app/productos/detalle-producto.tsx",
    ),
]

LENGUAJES = {
    ".py": "python",
    ".ts": "ts",
    ".tsx": "ts",
    ".json": "json",
    ".sql": "sql",
    ".css": "css",
    ".html": "html",
    ".md": "md",
}


# La demo se ejecuta en una carpeta temporal; en la página se muestra una ruta
# típica de un alumno en Windows.
CARPETA_EJEMPLO = "C:\\Users\\alumno"
_base_actual = ""


def _limpiar(texto: str) -> str:
    if _base_actual:
        texto = re.sub(re.escape(_base_actual) + r"[/\\]?([^\s]*)", lambda m: CARPETA_EJEMPLO + "\\" + m.group(1).replace("/", "\\"), texto)
    return texto


def _ejecutar(argumentos: list[str]) -> str:
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
        main(argumentos)
    return _limpiar(salida.getvalue().rstrip("\n"))


def _instantanea(carpeta: Path) -> dict[str, bytes]:
    return {
        p.relative_to(carpeta).as_posix(): p.read_bytes()
        for p in sorted(carpeta.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


def _lenguaje(ruta: str) -> str:
    return LENGUAJES.get(Path(ruta).suffix, "texto")


def _contenido(ruta: str, datos: bytes) -> str | None:
    if ruta.endswith(".png"):
        return None
    texto = datos.decode("utf-8")
    if ruta == ".env":
        texto = re.sub(r"^SECRET_KEY=.*$", "SECRET_KEY=(se genera al azar al crear el proyecto)", texto, flags=re.M)
    if not texto:
        texto = "(archivo vacío: sirve para que git guarde la carpeta)" if ruta.endswith(".gitkeep") else ""
    return texto


def demo_stack(base: Path, clave: str, titulo: str, carpeta: str, comandos: list[str], destacado: str) -> dict:
    os.chdir(base)
    pasos = [{"comando": f"andamio crear {clave} {carpeta}", "salida": _ejecutar(["crear", clave, carpeta])}]
    proyecto = base / carpeta
    os.chdir(proyecto)
    estado = {ruta: "proyecto" for ruta in _instantanea(proyecto)}
    for comando in comandos:
        antes = _instantanea(proyecto)
        pasos.append({"comando": f"andamio {comando}", "salida": _ejecutar(shlex.split(comando))})
        for ruta, datos in _instantanea(proyecto).items():
            if ruta not in antes:
                estado[ruta] = "nuevo"
            elif antes[ruta] != datos and estado.get(ruta) == "proyecto":
                estado[ruta] = "modificado"
    archivos = []
    for ruta, datos in _instantanea(proyecto).items():
        contenido = _contenido(ruta, datos)
        if contenido is not None:
            archivos.append({"ruta": ruta, "lenguaje": _lenguaje(ruta), "estado": estado[ruta], "contenido": contenido})
    return {"clave": clave, "titulo": titulo, "carpeta": carpeta, "pasos": pasos, "archivos": archivos, "destacado": destacado}


def demo_menu(base: Path) -> list[dict]:
    """Una sesión real del menú interactivo: lo que se ve y lo que escribe el alumno."""
    os.chdir(base)
    _ejecutar(["crear", "django", "mi-api"])
    os.chdir(base / "mi-api")
    respuestas = ["1", "producto", "", "nombre", "1", "precio", "4", "stock", "3", "", "s", "n"]
    eventos: list[dict] = []
    salida = io.StringIO()

    def volcar() -> None:
        texto = salida.getvalue()
        if texto:
            eventos.append({"tipo": "salida", "texto": _limpiar(texto)})
            salida.seek(0)
            salida.truncate()

    def falso_input(pregunta: str = "") -> str:
        volcar()
        respuesta = respuestas.pop(0)
        eventos.append({"tipo": "entrada", "pregunta": pregunta, "respuesta": respuesta})
        return respuesta

    original = builtins.input
    builtins.input = falso_input
    try:
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            main([])
    finally:
        builtins.input = original
    volcar()
    return eventos


def generar() -> dict:
    global _base_actual
    # Con los códigos de color ANSI que ve el alumno; la página los convierte a HTML.
    consola._usar_color = True
    cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as temporal:
            menu = Path(temporal) / "menu"
            stacks = Path(temporal) / "stacks"
            menu.mkdir()
            stacks.mkdir()
            _base_actual = str(menu.resolve())
            sesion = demo_menu(menu)
            _base_actual = str(stacks.resolve())
            demos = [demo_stack(stacks, *demo) for demo in DEMOS]
            return {"version": andamio.__version__, "menu": sesion, "stacks": demos}
    finally:
        _base_actual = ""
        os.chdir(cwd)


def main_sitio() -> None:
    datos = generar()
    texto = "// Generado por scripts/sitio.py: no editar a mano.\nwindow.ANDAMIO = " + json.dumps(
        datos, ensure_ascii=False, indent=1
    ) + ";\n"
    DESTINO.write_text(texto, encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)}  ({len(texto) // 1024} KB)")


if __name__ == "__main__":
    main_sitio()
