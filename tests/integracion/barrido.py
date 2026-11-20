"""Barrido de nombres riesgosos.

Cada identificador que usan las plantillas de una pieza (y las del proyecto, donde la
pieza se conecta) se prueba como nombre de la pieza y como nombre de campo. Por cada
uno, andamio tiene que rechazarlo con un mensaje claro o generar código que compile:
nunca código roto.

Qué se controla en lo generado:
- Python: que compile y que ningún nombre se defina dos veces en el mismo lugar
  (un import tapado por otro import, una función o una clase).
- JavaScript, TypeScript, JSX y Vue (el <script>): con el compilador de TypeScript,
  errores de sintaxis y nombres declarados dos veces. Hace falta `typescript` instalado
  en Node (npm install -g typescript); si no está, esa parte se saltea.
- HTML, JSX y Vue: que no haya dos elementos con el mismo id.

Se usa desde test_barrido.py y también a mano, para investigar una pieza:

    python -m tests.integracion.barrido fastapi recurso
    python -m tests.integracion.barrido react crud --variante js --campos
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from andamio import stacks
from andamio.cli import main
from andamio.nucleo import plantillas
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.generador import archivos_proyecto, carpeta_pieza
from andamio.nucleo.motor import MARCADOR
from andamio.nucleo.nombres import separar_palabras

NODE = shutil.which("node")

# Piezas cuyo nombre se elige de una lista fija (colores, partes de ui): no tiene
# sentido probar otros nombres.
NOMBRE_DE_LISTA = {"tema", "ui"}

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_COMENTARIO = re.compile(r"^\s*(#|//|\*|/\*|\{/\*|<!--|\{#)")
_ID_HTML = re.compile(r"""\bid=["']([A-Za-z][\w-]*)["']""")
_SCRIPT_VUE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.S)
_EXT_JS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
_IGNORADAS = {"node_modules", ".git", "__pycache__", ".web", ".next", "dist", ".venv"}


# --- Candidatos ---------------------------------------------------------------------------


def _textos(stack, pieza, variante: str) -> list[str]:
    archivos = plantillas.leer_arbol(carpeta_pieza(stack, pieza, variante)) + archivos_proyecto(stack, variante)
    return [a.texto for a in archivos if a.texto is not None]


def candidatos(stack, pieza, variante: str = "") -> list[str]:
    """Los identificadores de las plantillas (y sus singulares), como nombres para probar."""
    tokens: set[str] = set()
    for texto in _textos(stack, pieza, variante):
        for linea in texto.splitlines():
            if not _COMENTARIO.match(linea):
                tokens.update(_TOKEN.findall(MARCADOR.sub(" ", linea)))
    nombres: dict[tuple[str, ...], str] = {}
    for token in sorted(tokens):
        if len(token) < 3 or token.isupper() or token.startswith("_") or token[0].isdigit():
            continue
        formas = [token]
        for sufijo in ("es", "s"):
            if token.endswith(sufijo) and len(token) - len(sufijo) >= 3:
                formas.append(token[: -len(sufijo)])
        for forma in formas:
            try:
                nombres.setdefault(tuple(separar_palabras(forma)), forma)
            except AndamioError:
                pass
    return sorted(nombres.values())


# --- Ejecución ----------------------------------------------------------------------------


def _andamio(*argumentos: str) -> tuple[int, str]:
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
        codigo = main(list(argumentos))
    return codigo, salida.getvalue()


def _foto(raiz: Path) -> dict[Path, tuple[int, int]]:
    fotos: dict[Path, tuple[int, int]] = {}
    for carpeta, subcarpetas, archivos in os.walk(raiz):
        subcarpetas[:] = [s for s in subcarpetas if s not in _IGNORADAS]
        for archivo in archivos:
            ruta = Path(carpeta, archivo)
            datos = ruta.stat()
            fotos[ruta] = (datos.st_mtime_ns, datos.st_size)
    return fotos


@dataclass
class Resultado:
    generados: list[str] = field(default_factory=list)
    rechazados: dict[str, str] = field(default_factory=dict)
    problemas: list[str] = field(default_factory=list)

    def resumen(self) -> str:
        return f"{len(self.generados)} generados, {len(self.rechazados)} rechazados, {len(self.problemas)} problemas"


def barrer(
    stack_clave: str,
    pieza_clave: str,
    carpeta: Path,
    variante: str = "",
    campos: bool = False,
    nombres: list[str] | None = None,
) -> Resultado:
    """Crea un proyecto en `carpeta` y genera la pieza con cada nombre (o con cada campo)."""
    stack = stacks.por_clave(stack_clave)
    pieza = stack.piezas[pieza_clave]
    lista = nombres if nombres is not None else candidatos(stack, pieza, variante)
    anterior = os.getcwd()
    os.chdir(carpeta)
    resultado = Resultado()
    try:
        extra = ["--variante", variante] if variante else []
        codigo, salida = _andamio("crear", stack_clave, "barrido", *extra)
        assert codigo == 0, salida
        raiz = carpeta / "barrido"
        os.chdir(raiz)
        tocados: dict[str, list[Path]] = {}
        vistos: set[str] = set()
        for indice, candidato in enumerate(lista, 1):
            if campos:
                argumentos = ["nuevo", pieza_clave, f"ficha {indice}", f"{candidato}:str"]
            else:
                argumentos = ["nuevo", pieza_clave, candidato, *(["dato:str"] if pieza.usa_campos else [])]
            antes = _foto(raiz)
            codigo, salida = _andamio(*argumentos)
            if "error inesperado" in salida:
                resultado.problemas.append(f"[{candidato}] error inesperado de andamio:\n{salida}")
                continue
            if codigo != 0:
                resultado.rechazados[candidato] = salida.strip().splitlines()[0] if salida.strip() else "?"
                continue
            resultado.generados.append(candidato)
            despues = _foto(raiz)
            tocados[candidato] = [r for r, f in despues.items() if antes.get(r) != f]
            for ruta in tocados[candidato]:
                for problema in revisar_archivo(ruta, raiz):
                    # Un archivo compartido (App.tsx) que ya tenía el problema no se vuelve a contar.
                    if problema not in vistos:
                        vistos.add(problema)
                        resultado.problemas.append(f"[{candidato}] {problema}")
        resultado.problemas.extend(dict.fromkeys(revisar_js(raiz, tocados)))
    finally:
        os.chdir(anterior)
    return resultado


# --- Revisiones ---------------------------------------------------------------------------


def _ligaduras(cuerpo: list[ast.stmt], parametros: list[str]) -> dict[str, list[str]]:
    """Qué nombres define cada sentencia de un bloque (sin entrar en if/try/for)."""
    ligaduras: dict[str, list[str]] = {p: ["parámetro"] for p in parametros}
    for nodo in cuerpo:
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            for alias in nodo.names:
                nombre = alias.asname or alias.name.split(".")[0]
                if nombre != "*":
                    ligaduras.setdefault(nombre, []).append("import")
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            ligaduras.setdefault(nodo.name, []).append("def" if not isinstance(nodo, ast.ClassDef) else "class")
        elif isinstance(nodo, (ast.Assign, ast.AnnAssign)):
            objetivos = nodo.targets if isinstance(nodo, ast.Assign) else [nodo.target]
            for objetivo in objetivos:
                if isinstance(objetivo, ast.Name):
                    ligaduras.setdefault(objetivo.id, []).append("variable")
    return ligaduras


def _redefiniciones(arbol: ast.AST) -> list[str]:
    problemas = []
    bloques: list[tuple[str, list[ast.stmt], list[str]]] = [("módulo", arbol.body, [])]
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = nodo.args
            parametros = [a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]]
            parametros += [a.arg for a in (args.vararg, args.kwarg) if a is not None]
            bloques.append((f"función {nodo.name}", nodo.body, parametros))
        elif isinstance(nodo, ast.ClassDef):
            bloques.append((f"clase {nodo.name}", nodo.body, []))
    for donde, cuerpo, parametros in bloques:
        for nombre, tipos in _ligaduras(cuerpo, parametros).items():
            if len(tipos) > 1 and any(t != "variable" for t in tipos):
                problemas.append(f"'{nombre}' se define {len(tipos)} veces en {donde} ({', '.join(tipos)})")
    return problemas


def revisar_archivo(ruta: Path, raiz: Path) -> list[str]:
    rel = ruta.relative_to(raiz).as_posix()
    try:
        texto = ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    problemas = []
    if ruta.suffix == ".py":
        try:
            arbol = ast.parse(texto, filename=rel)
            compile(arbol, rel, "exec")
        except SyntaxError as e:
            return [f"{rel}:{e.lineno}: {e.msg}"]
        problemas += [f"{rel}: {p}" for p in _redefiniciones(arbol)]
    if ruta.suffix in {".html", ".vue", ".jsx", ".tsx"}:
        ids = _ID_HTML.findall(texto)
        repetidos = sorted({i for i in ids if ids.count(i) > 1})
        if repetidos:
            problemas.append(f"{rel}: id repetido en el HTML: {', '.join(repetidos)}")
    return problemas


_VERIFICADOR_TS = r"""
const ts = require('typescript');
const archivos = JSON.parse(require('fs').readFileSync(0, 'utf8'));
// Errores de nombres declarados dos veces (y de sintaxis). Los demás (módulos que no
// están instalados, tipos) no se miran: el proyecto no tiene node_modules.
const CODIGOS = new Set([2300, 2323, 2393, 2395, 2440, 2448, 2449, 2451, 2814, 18004]);
const programa = ts.createProgram(archivos, {
  allowJs: true, checkJs: true, noEmit: true, noResolve: true, skipLibCheck: true, types: [],
  jsx: ts.JsxEmit.Preserve, target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext,
});
for (const archivo of archivos) {
  const fuente = programa.getSourceFile(archivo);
  if (!fuente) continue;
  const diagnosticos = [
    ...programa.getSyntacticDiagnostics(fuente),
    ...programa.getSemanticDiagnostics(fuente).filter((d) => CODIGOS.has(d.code)),
  ];
  for (const d of diagnosticos) {
    const { line } = fuente.getLineAndCharacterOfPosition(d.start || 0);
    const texto = fuente.text.split('\n')[line] || '';
    console.log(JSON.stringify({ archivo, linea: line + 1, texto, mensaje: ts.flattenDiagnosticMessageText(d.messageText, ' ') }));
  }
}
"""


def hay_typescript() -> bool:
    if NODE is None:
        return False
    return subprocess.run([NODE, "-e", "require('typescript')"], capture_output=True).returncode == 0


def revisar_js(raiz: Path, tocados: dict[str, list[Path]]) -> list[str]:
    """Revisa con el compilador de TypeScript los archivos JS/TS/Vue que cambiaron."""
    if not hay_typescript():
        return []
    duenio: dict[Path, list[str]] = {}
    archivos: list[Path] = []
    for nombre, rutas in tocados.items():
        for ruta in rutas:
            if ruta.suffix == ".vue":
                ruta = _extraer_script_vue(ruta)
                if ruta is None:
                    continue
            elif ruta.suffix not in _EXT_JS:
                continue
            duenio.setdefault(ruta, []).append(nombre)
            if ruta not in archivos:
                archivos.append(ruta)
    if not archivos:
        return []
    proceso = subprocess.run(
        [NODE, "-e", _VERIFICADOR_TS],
        input=json.dumps([str(a) for a in archivos]),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proceso.returncode != 0:
        return [f"falló el verificador de TypeScript: {proceso.stderr[-2000:]}"]
    problemas = []
    for linea in proceso.stdout.splitlines():
        d = json.loads(linea)
        ruta = Path(d["archivo"])
        nombres = duenio.get(ruta, ["?"])
        # En un archivo compartido (App.tsx), el culpable es el nombre que aparece en la línea.
        culpables = [n for n in nombres if _aparece(n, d["texto"])] or nombres
        rel = ruta.relative_to(raiz).as_posix()
        problemas.append(f"[{', '.join(culpables)}] {rel}:{d['linea']}: {d['mensaje']}")
    return problemas


def _aparece(nombre: str, texto: str) -> bool:
    palabras = separar_palabras(nombre)
    return any(p in texto.lower() for p in ("".join(palabras), "_".join(palabras), "-".join(palabras)))


def _extraer_script_vue(ruta: Path) -> Path | None:
    bloques = _SCRIPT_VUE.findall(ruta.read_text(encoding="utf-8"))
    if not bloques:
        return None
    ts = any('lang="ts"' in atributos for atributos, _ in bloques)
    destino = ruta.with_name(ruta.name + (".ts" if ts else ".js"))
    destino.write_text("\n".join(codigo for _, codigo in bloques), encoding="utf-8")
    return destino


# --- Uso a mano ---------------------------------------------------------------------------


def _principal() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stack")
    parser.add_argument("pieza")
    parser.add_argument("--variante", default="")
    parser.add_argument("--campos", action="store_true", help="prueba los nombres como campos")
    parser.add_argument("--nombres", nargs="*", help="solo estos nombres")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        resultado = barrer(args.stack, args.pieza, Path(tmp), args.variante, args.campos, args.nombres)
    print(resultado.resumen())
    for problema in resultado.problemas:
        print("  " + problema)
    return 1 if resultado.problemas else 0


if __name__ == "__main__":
    sys.exit(_principal())
