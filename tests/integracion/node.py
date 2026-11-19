"""Ayudas para los tests que usan Node (solo se ejecutan con --lento)."""

import os
import shutil
import subprocess

import pytest

NPM = shutil.which("npm")
NPX = shutil.which("npx")
requiere_node = pytest.mark.skipif(NPM is None or NPX is None, reason="no hay Node/npm instalado")


def ejecutar(comando, cwd, env=None, timeout=900):
    resultado = subprocess.run(
        comando,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env={**os.environ, "CI": "1", **(env or {})},
    )
    assert resultado.returncode == 0, f"{' '.join(comando)}\n{resultado.stdout[-3000:]}\n{resultado.stderr[-3000:]}"
    return resultado


def npm_install(cwd):
    return ejecutar([NPM, "install", "--no-audit", "--no-fund", "--loglevel=error"], cwd)
