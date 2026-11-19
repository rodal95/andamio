"""Stack `python`: aplicación de consola con Python y sqlite3."""

from __future__ import annotations

import builtins
from pathlib import Path

from andamio.nucleo.nombres import Nombre
from andamio.stacks.base import Insercion, Pieza, Solicitud, Stack

TIPOS = {
    "str": "texto",
    "int": "número entero",
    "float": "número con decimales",
}

TIPOS_SQL = {"str": "TEXT", "int": "INTEGER", "float": "REAL"}


def _detectar(raiz: Path) -> bool:
    return (raiz / "main.py").is_file() and (raiz / "db.py").is_file()


def _contexto_entidad(sol: Solicitud) -> dict[str, str]:
    nombres = [c.nombre for c in sol.campos]
    return {
        "parametros": ", ".join(nombres),
        "columnas": ", ".join(nombres),
        "signos": ", ".join("?" for _ in nombres),
        # Una tupla de un solo elemento necesita la coma final: (nombre,)
        "valores": "(" + ", ".join(nombres) + ("," if len(nombres) == 1 else "") + ")",
        "asignaciones": ", ".join(f"{n} = ?" for n in nombres),
        "columnas_sql": ",\n".join(f"{c.nombre} {TIPOS_SQL[c.tipo]} NOT NULL" for c in sol.campos),
        "pedir_campos": "\n".join(f'{c.nombre} = pedir("{c.titulo}", {c.tipo})' for c in sol.campos),
        "pedir_campos_actual": "\n".join(
            f'{c.nombre} = pedir("{c.titulo}", {c.tipo}, actual["{c.nombre}"])' for c in sol.campos
        ),
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


ENTIDAD = Pieza(
    clave="entidad",
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
    reservados=lambda raiz: {
        "db": "ya existe el archivo db.py",
        "main": "ya existe el archivo main.py",
        "entrada": "ya existe menus/entrada.py",
    },
)
