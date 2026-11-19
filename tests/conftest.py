"""Configuración común de los tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from andamio import stacks
from andamio.nucleo import consola
from andamio.stacks.base import Insercion, Pieza, Stack


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--lento", action="store_true", help="ejecuta npm install y builds (necesita Node)")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--lento"):
        return
    saltear = pytest.mark.skip(reason="test lento: usá --lento para ejecutarlo")
    for item in items:
        if "lento" in item.keywords:
            item.add_marker(saltear)


@pytest.fixture(autouse=True)
def _sin_color(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(consola, "_usar_color", False)


@pytest.fixture
def respuestas(monkeypatch: pytest.MonkeyPatch):
    """Simula lo que el alumno escribe en el menú: respuestas(["1", "producto", ...])."""

    def configurar(lista: list[str]) -> list[str]:
        pendientes = list(lista)
        preguntas: list[str] = []

        def falso_input(texto: str = "") -> str:
            preguntas.append(texto)
            if not pendientes:
                raise EOFError
            return pendientes.pop(0)

        monkeypatch.setattr("builtins.input", falso_input)
        return preguntas

    return configurar


def _escribir(base: Path, rel: str, texto: str) -> None:
    ruta = base / rel
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


@pytest.fixture
def stack_prueba(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Stack:
    """Un stack mínimo con plantillas en una carpeta temporal, registrado como único stack."""
    base = tmp_path / "_plantillas"
    _escribir(base, "_proyecto/main.txt", "Proyecto @@proyectoTitulo@@\n    # --- andamio:items (no borrar esta línea) ---\n")
    _escribir(base, "_proyecto/.env.example", "CLAVE=@@clave@@\n")
    _escribir(base, "_proyecto/gitignore", "*.log\n")
    _escribir(base, "cosa/cosas/@@nombre@@.txt", "Clase @@Nombre@@\n    @@lista@@\nFin\n")
    _escribir(base, "cosa/comun.txt", "compartido\n")
    _escribir(base, "cosa/LEEME.md", "no se genera\n")

    def contexto(sol) -> dict[str, str]:
        return {"lista": "\n".join(f"{c.nombre}: {c.tipo}" for c in sol.campos)}

    pieza = Pieza(
        clave="cosa",
        titulo="Cosa",
        descripcion="una cosa de prueba",
        ejemplo="producto nombre:str",
        formas=("pascal", "snake"),
        usa_campos=True,
        usa_plural=True,
        contexto=contexto,
        existe_si=("cosas/@@nombre@@.txt",),
        si_no_existe=frozenset({"comun.txt"}),
        inserciones=(
            Insercion("main.txt", "item @@nombre@@ (@@plural@@)", marcador="items", descripcion="item @@nombre@@"),
            Insercion("lista.txt", "@@nombre@@", crear_si_falta=True),
        ),
        siguiente_paso=["usar @@nombre@@"],
    )
    stack = Stack(
        clave="prueba",
        titulo="Prueba",
        senal="main.txt",
        detectar=lambda raiz: (raiz / "main.txt").is_file(),
        tipos={"str": "texto", "int": "número entero"},
        piezas={"cosa": pieza},
        ejemplo_proyecto="mi-prueba",
        siguiente_paso_proyecto=["cd @@carpeta@@"],
        contexto_env=lambda: {"clave": "secreta"},
        contexto_proyecto=lambda nombre: {"clave": "cambiar"},
        plantillas=base,
    )
    monkeypatch.setattr(stacks, "REGISTRO", [stack])
    monkeypatch.setattr(stacks, "ORDEN_MENU", [stack])
    return stack


@pytest.fixture
def en_carpeta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Directorio de trabajo vacío para crear proyectos."""
    carpeta = tmp_path / "trabajo"
    carpeta.mkdir()
    monkeypatch.chdir(carpeta)
    return carpeta

