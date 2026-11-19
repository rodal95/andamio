"""`python -m andamio configurar`: hace que el comando `andamio` funcione solo.

Cuando pip instala andamio "para el usuario" (lo normal en una PC sin permisos de
administrador), deja `andamio.exe` en una carpeta que Windows no conoce. Por eso
`andamio` no se reconoce y hay que escribir `python -m andamio`.

Este comando busca esa carpeta y la agrega al PATH del usuario (en el registro de
Windows, sin permisos de administrador). Es opcional: `python -m andamio` funciona
siempre. En Linux y Mac solo explica qué línea agregar, para no tocar archivos de
configuración de la terminal.
"""

from __future__ import annotations

import os
from importlib import metadata
from pathlib import Path

from andamio.nucleo import consola
from andamio.nucleo.errores import AndamioError

_EJECUTABLES = {"andamio", "andamio.exe"}


def carpeta_de_andamio() -> Path | None:
    """La carpeta donde pip dejó el comando `andamio`, según el registro de la instalación."""
    try:
        distribucion = metadata.distribution("andamio")
    except metadata.PackageNotFoundError:
        return None
    for archivo in distribucion.files or []:
        if archivo.name.lower() in _EJECUTABLES and archivo.parent.name.lower() in ("scripts", "bin"):
            ruta = Path(distribucion.locate_file(archivo)).resolve()
            if ruta.is_file():
                return ruta.parent
    return None


def _normalizar(ruta: str) -> str:
    return os.path.normcase(os.path.normpath(os.path.expandvars(ruta.strip().strip('"'))))


def esta_en_path(carpeta: Path, valor_path: str) -> bool:
    buscada = _normalizar(str(carpeta))
    return any(_normalizar(parte) == buscada for parte in valor_path.split(os.pathsep) if parte.strip())


def agregar_a_path(valor_path: str, carpeta: Path) -> str:
    valor = valor_path.rstrip(os.pathsep)
    return f"{valor}{os.pathsep}{carpeta}" if valor else str(carpeta)


# --- Registro de Windows (PATH del usuario) -------------------------------------


def leer_path_usuario() -> tuple[str, int]:
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as clave:
        try:
            valor, tipo = winreg.QueryValueEx(clave, "Path")
        except FileNotFoundError:
            return "", winreg.REG_EXPAND_SZ
    return str(valor), tipo


def escribir_path_usuario(valor: str, tipo: int) -> None:
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as clave:
        winreg.SetValueEx(clave, "Path", 0, tipo, valor)
    _avisar_a_windows()


def _avisar_a_windows() -> None:
    """Avisa que cambió el entorno, para que las terminales nuevas tomen el PATH nuevo."""
    try:
        import ctypes
        from ctypes import wintypes

        resultado = wintypes.DWORD()
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, ctypes.byref(resultado))
    except Exception:  # no es grave: igual hay que abrir una terminal nueva
        pass


# --- Comando --------------------------------------------------------------------


def es_windows() -> bool:
    return os.name == "nt"


def configurar(simular: bool = False, windows: bool | None = None) -> int:
    windows = es_windows() if windows is None else windows
    carpeta = carpeta_de_andamio()
    if carpeta is None:
        raise AndamioError(
            "No encontré el comando andamio instalado: lo estás usando sin instalar (andamio.pyz o la carpeta descomprimida).",
            f"Seguí usándolo así ({consola.programa()} ...), o instalalo con python -m pip install y después ejecutá: "
            "python -m andamio configurar",
        )

    if not windows:
        if esta_en_path(carpeta, os.environ.get("PATH", "")):
            consola.exito("Ya está configurado: podés escribir andamio en lugar de python -m andamio.")
            return 0
        consola.escribir("En Linux o Mac, agregá esta línea al final de ~/.bashrc (o ~/.zshrc si usás zsh):")
        consola.escribir()
        consola.escribir("    " + consola.comando(f'export PATH="$PATH:{carpeta}"'))
        consola.escribir()
        consola.escribir("Después abrí una terminal nueva. Mientras tanto, python -m andamio funciona igual.")
        return 0

    valor, tipo = leer_path_usuario()
    if esta_en_path(carpeta, valor):
        consola.exito("Ya está configurado.")
        consola.escribir(
            "Si andamio todavía no se reconoce, cerrá la terminal (y VS Code, si lo usás) y abrí una nueva."
        )
        return 0

    consola.escribir(f"Carpeta de andamio: {consola.color(str(carpeta), 'negrita')}")
    if simular:
        consola.escribir()
        consola.escribir(consola.color("Simulación: se agregaría esa carpeta al PATH de tu usuario. No se cambió nada.", "amarillo", "negrita"))
        return 0
    try:
        escribir_path_usuario(agregar_a_path(valor, carpeta), tipo)
    except OSError as e:
        raise AndamioError(
            f"No se pudo modificar el PATH de tu usuario ({e.strerror or e}).",
            "No pasa nada: seguí usando python -m andamio, que funciona igual.",
        ) from e
    consola.escribir()
    consola.exito("Listo. Agregué esa carpeta al PATH de tu usuario (no hizo falta ser administrador).")
    consola.escribir()
    consola.titulo("Siguiente paso:")
    consola.escribir("    Cerrá esta terminal (y VS Code, si lo usás) y abrí una nueva. Desde ahí podés escribir:")
    consola.escribir("    " + consola.comando("andamio --version"))
    consola.escribir()
    consola.escribir(consola.color("python -m andamio sigue funcionando igual, en cualquier terminal.", "gris"))
    return 0
