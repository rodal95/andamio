"""Stack `python`: aplicación de consola con Python y sqlite3."""

from __future__ import annotations

import builtins
from pathlib import Path

from andamio.nucleo import relaciones
from andamio.nucleo.errores import AndamioError
from andamio.nucleo.nombres import Nombre
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

TIPOS = {
    "str": "texto",
    "int": "número entero",
    "float": "número con decimales",
    relaciones.TIPO: relaciones.descripcion("otra entidad"),
}

TIPOS_SQL = {"str": "TEXT", "int": "INTEGER", "float": "REAL"}


def _detectar(raiz: Path) -> bool:
    if not ((raiz / "main.py").is_file() and (raiz / "db.py").is_file()):
        return False
    # app/ de un proyecto FastAPI también tiene main.py y db.py: no es de consola.
    try:
        return "fastapi" not in (raiz / "main.py").read_text(encoding="utf-8-sig").lower()
    except (OSError, UnicodeDecodeError):
        return True


def _relaciones(sol: Solicitud) -> list[relaciones.Relacion]:
    """Los campos :fk, controlando que exista la entidad a la que apuntan."""
    lista = relaciones.de_campos(sol.raiz, sol.campos, sol.nombre, ("entidad",))
    for rel in lista:
        if not (sol.raiz / "entidades" / f"{rel.campo.nombre}.py").is_file():
            raise relaciones.falta(rel.campo, f"la entidad '{rel.campo.nombre}'", f"python -m andamio nuevo entidad {rel.campo.nombre} nombre:str")
    return lista


def _sql_listar(sol: Solicitud, rels: list[relaciones.Relacion]) -> str:
    """SELECT de listar(): con un JOIN por relación, para mostrar su texto en lugar del id."""
    tabla = sol.nombre.plural
    con_texto = [r for r in rels if r.texto]
    if not con_texto:
        return f"SELECT * FROM {tabla} ORDER BY id"
    columnas = ", ".join(f"{r.destino.plural}.{r.texto} AS {r.campo.nombre}" for r in con_texto)
    uniones = " ".join(f"LEFT JOIN {r.destino.plural} ON {r.destino.plural}.id = {tabla}.{r.campo.nombre}_id" for r in con_texto)
    return f"SELECT {tabla}.*, {columnas} FROM {tabla} {uniones} ORDER BY {tabla}.id"


_PEDIR_RELACION = """

def pedir_{n}(actual=None):
    \"\"\"Muestra {titulo} y pide el id de una (tiene que existir).\"\"\"
    mostrar_filas({n}.listar())
    while True:
        id_{n} = pedir("Id de {n}", int, actual)
        if {n}.obtener(id_{n}) is not None:
            return id_{n}
        print("  No existe ese id: elegí uno de la lista.")"""


def _columna(campo) -> str:
    """El nombre de la columna (y de la variable): categoria:fk se guarda en categoria_id."""
    return f"{campo.nombre}_id" if campo.tipo == relaciones.TIPO else campo.nombre


def _columna_sql(campo, destinos: dict) -> str:
    if campo.nombre in destinos:
        # ON DELETE SET NULL: si se borra la categoría, el producto queda sin categoría.
        return f"{campo.nombre}_id INTEGER REFERENCES {destinos[campo.nombre].plural}(id) ON DELETE SET NULL"
    return f"{campo.nombre} {TIPOS_SQL[campo.tipo]} NOT NULL"


def _pedir(campo, actual: bool) -> str:
    if campo.tipo == relaciones.TIPO:
        return f'{campo.nombre}_id = pedir_{campo.nombre}({f"actual[{chr(34)}{campo.nombre}_id{chr(34)}]" if actual else ""})'
    return f'{campo.nombre} = pedir("{campo.titulo}", {campo.tipo}{f", actual[{chr(34)}{campo.nombre}{chr(34)}]" if actual else ""})'


def _contexto_entidad(sol: Solicitud) -> dict[str, str]:
    rels = _relaciones(sol)
    destinos = {r.campo.nombre: r.destino for r in rels}
    nombres = [_columna(c) for c in sol.campos]
    return {
        "sql_listar": _sql_listar(sol, rels),
        "imports_relaciones": "\n".join(f"from entidades import {r.campo.nombre}" for r in rels),
        "funciones_relaciones": "".join(
            _PEDIR_RELACION.format(n=r.campo.nombre, titulo=" ".join(r.destino.plural_palabras)) for r in rels
        ),
        "parametros": ", ".join(nombres),
        "columnas": ", ".join(nombres),
        "signos": ", ".join("?" for _ in nombres),
        # Una tupla de un solo elemento necesita la coma final: (nombre,)
        "valores": "(" + ", ".join(nombres) + ("," if len(nombres) == 1 else "") + ")",
        "asignaciones": ", ".join(f"{n} = ?" for n in nombres),
        "columnas_sql": ",\n".join(_columna_sql(c, destinos) for c in sol.campos),
        "pedir_campos": "\n".join(_pedir(c, actual=False) for c in sol.campos),
        "pedir_campos_actual": "\n".join(_pedir(c, actual=True) for c in sol.campos),
    }


_FUNCIONES_PYTHON = {
    n: f"choca con la función '{n}' de Python" for n in dir(builtins) if n.islower() and not n.startswith("_")
}


def _campos_reservados(nombre: Nombre) -> dict[str, str]:
    # Los campos se usan como nombres de variable en el código generado:
    # no pueden pisar el módulo de la entidad ni las variables y funciones de las plantillas.
    reservados = dict(_FUNCIONES_PYTHON)
    for variable in ("conexion", "cursor", "fila", "filas", "actual", "opcion", "nuevo_id"):
        reservados[variable] = "es una variable que usa el código generado"
    for funcion in ("pedir", "confirmar", "mostrar_filas", "get_conexion"):
        reservados[funcion] = "es una función que usa el código generado"
    reservados[nombre.snake] = "tiene el mismo nombre que la entidad"
    reservados[f"id_{nombre.snake}"] = "es el nombre que se usa para el id"
    return reservados


_MODULOS_DEL_PROYECTO = {
    "db": "ya existe el archivo db.py",
    "main": "ya existe el archivo main.py",
    "entrada": "ya existe el archivo menus/entrada.py",
}


def _validar_nombre(raiz: Path, nombre: Nombre) -> None:
    motivo = _MODULOS_DEL_PROYECTO.get(nombre.snake)
    if motivo:
        raise AndamioError(f"No se puede usar '{nombre.snake}': {motivo}.", "Elegí otro nombre.")


ENTIDAD = Pieza(
    clave="entidad",
    lectura=(
        ('sql/schema.sql', 'la tabla @@plural@@ (al final del archivo)'),
        ('entidades/@@nombre@@.py', 'guardar, listar, modificar y eliminar en SQLite'),
        ('menus/menu_@@nombre@@.py', 'el menú de consola que usa la entidad'),
        ('main.py', 'el menú principal, con la opción nueva'),
    ),
    titulo="Entidad",
    descripcion="tabla + funciones CRUD + menú de consola",
    ejemplo="producto nombre:str precio:float stock:int",
    formas=("snake",),
    usa_campos=True,
    usa_plural=True,
    contexto=_contexto_entidad,
    campos_reservados=_campos_reservados,
    marcadores={
        "parametros": "campos separados por coma: nombre, precio",
        "columnas": "columnas para el INSERT: nombre, precio",
        "signos": "un ? por campo: ?, ?",
        "valores": "tupla con los campos: (nombre, precio)",
        "asignaciones": "para el UPDATE: nombre = ?, precio = ?",
        "columnas_sql": "una línea por columna para el CREATE TABLE",
        "pedir_campos": 'una línea por campo: nombre = pedir("Nombre", str)',
        "pedir_campos_actual": 'igual, conservando el valor actual: pedir("Nombre", str, actual["nombre"])',
        "sql_listar": "el SELECT de listar(): con un LEFT JOIN por cada relación (campo:fk)",
        "imports_relaciones": "en el menú, el import de cada entidad relacionada (vacío sin campos :fk)",
        "funciones_relaciones": "en el menú, pedir_<relación>(): muestra la lista y pide un id que exista",
    },
    existe_si=("entidades/@@nombre@@.py", "menus/menu_@@nombre@@.py"),
    inserciones=(
        Insercion(
            "sql/schema.sql",
            "\n-- @@titulo@@\nCREATE TABLE IF NOT EXISTS @@plural@@ (\n"
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    @@columnas_sql@@\n);",
            descripcion="tabla @@plural@@",
            comentario="--",
        ),
        Insercion(
            "main.py",
            "from menus import menu_@@nombre@@",
            marcador="imports",
            descripcion="import del menú",
            ubicacion="arriba, junto a los otros import",
        ),
        Insercion(
            "main.py",
            '"@@titulo@@": menu_@@nombre@@.mostrar_menu,',
            marcador="menus",
            descripcion="opción en MENUS",
            ubicacion="dentro del diccionario MENUS = { ... }",
        ),
    ),
    siguiente_paso=["python main.py"],
)

STACK = Stack(
    clave="python",
    titulo="Python + SQLite",
    senal="main.py y db.py",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={"entidad": ENTIDAD},
    ejemplo_proyecto="mi-tienda",
    siguiente_paso_proyecto=["cd @@carpeta@@", "python main.py"],
    validar_nombre=_validar_nombre,
)
