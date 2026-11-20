"""Identificadores que declara el código de las plantillas.

Sirve para rechazar un nombre que el código generado ya usa para otra cosa: un recurso
"sesion" en FastAPI (la sesión de la base de datos se llama `sesion`), una página "app"
en Reflex (`app = rx.App()`), un crud "error" en Vue (`const error = ref(...)`).
Con esos nombres el código no compila, o compila y hace otra cosa.

Se miran solo las *declaraciones* (imports, funciones, clases, variables y parámetros),
no cualquier palabra: un nombre que aparece en un texto o en un comentario no molesta.
Lo que sale de un marcador (@@Nombre@@Crear) no cuenta, porque depende del nombre.
Funciona igual con las plantillas que el docente exportó y modificó.
"""

from __future__ import annotations

import ast
import re

from andamio.nucleo.motor import MARCADOR
from andamio.nucleo.nombres import Nombre, camel, pascal

_RELLENO = "zzmarcadorzz"  # reemplaza a cada marcador para poder analizar el código

_ID = r"[A-Za-z_$][\w$]*"
_IMPORT_DEFECTO = re.compile(rf"\bimport\s+(?:type\s+)?({_ID})\s*(?:,|\bfrom\b)")
_IMPORT_TODO = re.compile(rf"\bimport\s+\*\s+as\s+({_ID})")
_IMPORT_LLAVES = re.compile(r"\bimport\s+(?:type\s+)?(?:[\w$]+\s*,\s*)?\{([^}]*)\}")
_DECLARACION = re.compile(rf"\b(?:const|let|var|function\*?|class|interface|type|enum)\s+({_ID})")
_DESESTRUCTURACION = re.compile(r"\b(?:const|let|var)\s*[\[{]([^=;]*?)[\]}]\s*(?::[^=]+)?=")
_PARAMETROS_FUNCION = re.compile(r"\bfunction\b\s*\*?\s*[\w$]*\s*(?:<[^>]*>)?\s*\(([^)]*)\)")
_PARAMETROS_FLECHA = re.compile(r"\(([^()]*)\)\s*(?::\s*[^=;{]+?)?\s*=>")
_PARAMETRO_SOLO = re.compile(rf"(?<![\w$.])({_ID})\s*=>")


def _sin_marcadores(texto: str) -> str:
    return MARCADOR.sub(_RELLENO, texto)


def _validos(nombres) -> set[str]:
    # Lo que sale de un marcador (o del nombre centinela) no es un nombre fijo del código.
    return {n for n in nombres if n and _RELLENO not in n and "zq" not in n.lower() and n.isidentifier()}


# --- Python -----------------------------------------------------------------------------


_MARCADOR_SOLO = re.compile(r"(?m)^([ \t]*)@@[A-Za-z][A-Za-z0-9_]*@@[ \t]*$")


def _parsear_python(texto: str) -> ast.AST | None:
    # Un marcador solo en su línea se convierte en varias líneas de código (campos,
    # parámetros, sentencias): se prueba como comentario, como nombre y como `pass`.
    for reemplazo in (r"\1# marcador", rf"\1{_RELLENO}", r"\1pass"):
        try:
            return ast.parse(_sin_marcadores(_MARCADOR_SOLO.sub(reemplazo, texto)))
        except SyntaxError:
            continue
    return None


_PY_DEF = re.compile(rf"^\s*(?:async\s+)?(?:def|class)\s+({_ID})", re.M)
_PY_IMPORT = re.compile(r"^\s*(?:from\s+\S+\s+)?import\s+([^#\n(]+)", re.M)
_PY_ASIGNACION = re.compile(rf"^\s*({_ID})\s*(?::[^=\n]+)?=(?!=)", re.M)


def _python_aproximado(texto: str) -> set[str]:
    """Para plantillas que no se pueden analizar: imports, funciones, clases y variables."""
    codigo = _sin_marcadores(texto)
    nombres = _PY_DEF.findall(codigo) + _PY_ASIGNACION.findall(codigo)
    for lista in _PY_IMPORT.findall(codigo):
        nombres += [p.split(" as ")[-1].strip().split(".")[0] for p in lista.split(",")]
    return _validos(nombres)


def _python(texto: str) -> set[str]:
    arbol = _parsear_python(texto)
    if arbol is None:
        return _python_aproximado(texto)
    nombres: list[str] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.Import, ast.ImportFrom)):
            nombres += [a.asname or a.name.split(".")[0] for a in nodo.names if a.name != "*"]
        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.append(nodo.name)
        elif isinstance(nodo, ast.arg):
            nombres.append(nodo.arg)
        elif isinstance(nodo, ast.Name) and isinstance(nodo.ctx, ast.Store):
            nombres.append(nodo.id)
        elif isinstance(nodo, ast.ExceptHandler) and nodo.name:
            nombres.append(nodo.name)
    return _validos(nombres) - {"self", "cls", "_"}


# --- JavaScript, TypeScript, JSX y Vue --------------------------------------------------


def _partes(texto: str) -> list[str]:
    """Divide por las comas de primer nivel (no las de adentro de (), [], {} o <>)."""
    partes, profundidad, actual = [], 0, ""
    for caracter in texto.replace("=>", "→") + ",":
        if caracter in "([{<":
            profundidad += 1
        elif caracter in ")]}>":
            profundidad -= 1
        if caracter == "," and profundidad == 0:
            partes.append(actual.strip())
            actual = ""
        else:
            actual += caracter
    return [p for p in partes if p]


def _interior(texto: str) -> str:
    """Lo de adentro de {...} o [...] al principio del texto."""
    profundidad = 0
    for i, caracter in enumerate(texto):
        if caracter in "[{":
            profundidad += 1
        elif caracter in "]}":
            profundidad -= 1
            if profundidad == 0:
                return texto[1:i]
    return texto[1:]


def _lista(texto: str, desestructuracion: bool = False) -> list[str]:
    """Nombres de una lista como `a, b as c, d = 1, e: Tipo, { f, g: h }, ...i`
    (imports, parámetros y desestructuraciones)."""
    nombres: list[str] = []
    for parte in _partes(texto):
        parte = parte.lstrip(".").strip()
        if parte.startswith(("{", "[")):  # ({ a, b }: Props) o [a, setA]
            nombres += _lista(_interior(parte), desestructuracion=True)
            continue
        parte = parte.split("=")[0].strip()
        if " as " in parte:
            parte = parte.split(" as ")[1]
        elif ":" in parte:
            antes, despues = (s.strip() for s in parte.split(":", 1))
            if desestructuracion and despues.startswith(("{", "[")):
                nombres += _lista(_interior(despues), desestructuracion=True)
                continue
            # En una desestructuración {a: b} el nombre es b; en un parámetro (a: Tipo), es a.
            parte = despues if desestructuracion else antes
        parte = re.sub(r"^(?:type|readonly|public|private|protected)\s+", "", parte.strip()).rstrip("?").strip()
        nombres.append(parte)
    return nombres


def _javascript(texto: str) -> set[str]:
    codigo = _sin_marcadores(texto)
    if "<script" in codigo:  # componente de Vue: solo el código, no la plantilla HTML
        codigo = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", codigo, re.S))
    codigo = re.sub(r"/\*.*?\*/", " ", codigo, flags=re.S)
    codigo = re.sub(r"(?m)//.*$", " ", codigo)
    nombres: list[str] = []
    nombres += _IMPORT_DEFECTO.findall(codigo) + _IMPORT_TODO.findall(codigo) + _DECLARACION.findall(codigo)
    nombres += _PARAMETRO_SOLO.findall(codigo)
    for grupo in _IMPORT_LLAVES.findall(codigo):
        nombres += _lista(grupo)
    for grupo in _DESESTRUCTURACION.findall(codigo):
        nombres += _lista(grupo, desestructuracion=True)
    for grupo in [*_PARAMETROS_FUNCION.findall(codigo), *_PARAMETROS_FLECHA.findall(codigo)]:
        nombres += _lista(grupo)
    return _validos(nombres) - {"_"}


_EXTENSIONES_JS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue"}


def declarados(nombre_archivo: str, texto: str) -> set[str]:
    """Los identificadores que declara una plantilla (vacío si no es código)."""
    sufijo = "." + nombre_archivo.rsplit(".", 1)[-1] if "." in nombre_archivo else ""
    if sufijo == ".py":
        return _python(texto)
    if sufijo in _EXTENSIONES_JS:
        return _javascript(texto)
    return set()


# --- Conflictos con el nombre de una pieza -------------------------------------------------

# Para saber dónde el código usa el nombre, las plantillas se renderizan con un nombre
# "centinela" que no puede chocar con nada: todo lo que contenga "zq" viene del nombre.
CENTINELA = Nombre.desde_palabras(["zqz", "centinela"])

_FORMAS = ("snake", "camel", "pascal", "plural", "plural_camel", "plural_pascal")


def _forma(nombre: Nombre, forma: str) -> str:
    if forma == "plural_camel":
        return camel(nombre.plural_palabras)
    if forma == "plural_pascal":
        return pascal(nombre.plural_palabras)
    return getattr(nombre, forma)


def formas_usadas(texto_centinela: str, nombre: Nombre) -> set[str]:
    """Las formas del nombre que el código (renderizado con el centinela) usa como
    identificador completo: `zqz_centinela` suelto, no `id_zqz_centinela` ni `ZqzCentinelaCrear`."""
    usadas = set()
    for forma in _FORMAS:
        if re.search(rf"(?<![\w$]){re.escape(_forma(CENTINELA, forma))}(?![\w$])", texto_centinela):
            usadas.add(_forma(nombre, forma))
    return usadas


def conflicto(nombre_archivo: str, texto_centinela: str, nombre: Nombre, ocupados_extra: set[str] | None = None) -> str | None:
    """La forma del nombre que choca con un identificador que el archivo ya declara, o None."""
    usadas = formas_usadas(texto_centinela, nombre)
    if not usadas:
        return None
    ocupados = declarados(nombre_archivo, texto_centinela) | (ocupados_extra or set())
    chocan = sorted(usadas & ocupados)
    return chocan[0] if chocan else None
