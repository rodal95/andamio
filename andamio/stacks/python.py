"""Stack `python`: aplicación de consola con Python y sqlite3."""

from __future__ import annotations

import builtins
import dataclasses
from pathlib import Path

from andamio.nucleo import historial, relaciones
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


_ARCHIVO_MENU = "menus/menu_@@nombre@@.py"


def _con_menu(sol: Solicitud) -> bool:
    return not sol.opciones.get("sin_menu")


def _contexto_entidad_y_menu(sol: Solicitud) -> dict[str, str]:
    con_menu = _con_menu(sol)
    return {
        **_contexto_entidad(sol),
        # Para el orden de lectura: sin menú (--sin-menu) esos archivos no se tocan.
        "archivo_menu": f"menus/menu_{sol.nombre.snake}.py" if con_menu else "",
        "archivo_main": "main.py" if con_menu else "",
    }


_MARCADORES_ENTIDAD = {
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
}

# El menú se registra en main.py (el import y la opción en MENUS).
_INSERCIONES_MENU = (
    Insercion(
        "main.py",
        "from menus import menu_@@nombre@@",
        marcador="imports",
        descripcion="import del menú",
        ubicacion="arriba, junto a los otros import",
        condicion=_con_menu,
    ),
    Insercion(
        "main.py",
        '"@@titulo@@": menu_@@nombre@@.mostrar_menu,',
        marcador="menus",
        descripcion="opción en MENUS",
        ubicacion="dentro del diccionario MENUS = { ... }",
        condicion=_con_menu,
    ),
)

ENTIDAD = Pieza(
    clave="entidad",
    lectura=(
        ('sql/schema.sql', 'la tabla @@plural@@ (al final del archivo)'),
        ('entidades/@@nombre@@.py', 'guardar, listar, modificar y eliminar en SQLite'),
        ('@@archivo_menu@@', 'el menú de consola que usa la entidad'),
        ('@@archivo_main@@', 'el menú principal, con la opción nueva'),
    ),
    titulo="Entidad",
    descripcion="tabla + funciones CRUD + menú de consola (--sin-menu: solo la tabla y las funciones)",
    ejemplo="producto nombre:str precio:float stock:int",
    formas=("snake",),
    usa_campos=True,
    usa_plural=True,
    opciones=frozenset({"sin_menu"}),
    contexto=_contexto_entidad_y_menu,
    campos_reservados=_campos_reservados,
    marcadores={
        **_MARCADORES_ENTIDAD,
        "archivo_menu": "menus/menu_<nombre>.py (vacío con --sin-menu)",
        "archivo_main": "main.py (vacío con --sin-menu)",
    },
    existe_si=("entidades/@@nombre@@.py", _ARCHIVO_MENU),
    omitir=lambda sol: frozenset() if _con_menu(sol) else frozenset({_ARCHIVO_MENU}),
    inserciones=(
        Insercion(
            "sql/schema.sql",
            "\n-- @@titulo@@\nCREATE TABLE IF NOT EXISTS @@plural@@ (\n"
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    @@columnas_sql@@\n);",
            descripcion="tabla @@plural@@",
            comentario="--",
        ),
        *_INSERCIONES_MENU,
    ),
    siguiente_paso=lambda sol: ["python main.py"] if _con_menu(sol) else [
        "# Usá las funciones desde tu código:",
        "from entidades import @@nombre@@",
        "# Cuando quieras el menú de consola: python -m andamio nuevo menu @@nombre@@",
    ],
)


# --- Piezas que usan una entidad que ya existe ------------------------------------------


def _entidad_existente(sol: Solicitud, ejemplo: str) -> historial.Entrada:
    """La entidad (su archivo y, del historial, su plural y sus campos), o un error que explica."""
    nombre = sol.nombre.snake
    if not (sol.raiz / "entidades" / f"{nombre}.py").is_file():
        raise AndamioError(
            f"No existe la entidad '{nombre}' (entidades/{nombre}.py).",
            f"Generala primero: python -m andamio nuevo entidad {nombre} nombre:str precio:float --sin-menu",
        )
    entrada = historial.ultima(sol.raiz, nombre, ("entidad",))
    if entrada is None or not entrada.campos:
        raise AndamioError(
            f"No sé con qué campos se generó la entidad '{nombre}': no está en el historial de andamio ({historial.ARCHIVO}).",
            ejemplo,
        )
    return entrada


def _contexto_menu(sol: Solicitud) -> dict[str, str]:
    entrada = _entidad_existente(sol, "Escribí el menú a mano, o generá la entidad con andamio.")
    # El plural y los campos son los de la entidad (no hace falta repetirlos).
    return {**entrada.nombre.marcadores(), **_contexto_entidad(dataclasses.replace(sol, nombre=entrada.nombre, campos=entrada.campos))}


MENU = Pieza(
    clave="menu",
    lectura=(
        ('entidades/@@nombre@@.py', 'las funciones de la entidad, que usa el menú'),
        ('menus/menu_@@nombre@@.py', 'el menú de consola: listar, agregar, modificar y eliminar'),
        ('main.py', 'el menú principal, con la opción nueva'),
    ),
    titulo="Menú",
    descripcion="menú de consola para una entidad que ya existe (creada con --sin-menu)",
    ejemplo="cliente",
    preparar=("entidad cliente nombre:str email:str --sin-menu",),
    formas=("snake", "menu_@@nombre@@"),
    usa_existente=True,
    contexto=_contexto_menu,
    marcadores=_MARCADORES_ENTIDAD,
    existe_si=(_ARCHIVO_MENU,),
    inserciones=_INSERCIONES_MENU,
    siguiente_paso=["python main.py"],
)


_FUNCION_BUSQUEDA = """

def buscar_por_{c}(valor):
    \"\"\"{doc}\"\"\"
    with get_conexion() as conexion:
        filas = conexion.execute(
            "SELECT * FROM {tabla} WHERE {columna} {operador} ? ORDER BY id",
            ({parametro},),
        ).fetchall()
        return [dict(fila) for fila in filas]"""

_MENU_BUSQUEDA = """

def buscar_por_{c}():
    valor = pedir("{titulo} a buscar", {tipo})
    mostrar_filas({entidad}.buscar_por_{c}(valor))"""


def _contexto_busqueda(sol: Solicitud) -> dict[str, str]:
    entrada = _entidad_existente(sol, "Agregá la búsqueda a mano en entidades/ y en menus/.")
    campos = {c.nombre: c for c in entrada.campos}
    if not (sol.raiz / "menus" / f"menu_{sol.nombre.snake}.py").is_file():
        raise AndamioError(
            f"La entidad '{sol.nombre.snake}' no tiene menú (menus/menu_{sol.nombre.snake}.py): la búsqueda va en el menú.",
            f"Generá el menú primero: python -m andamio nuevo menu {sol.nombre.snake}",
        )
    for pedido in sol.campos:
        if pedido.nombre not in campos:
            raise AndamioError(
                f"La entidad '{sol.nombre.snake}' no tiene el campo '{pedido.nombre}'.",
                "Campos: " + ", ".join(campos),
            )
    pedidos = {c.nombre for c in sol.campos}
    funciones, funciones_menu, opciones, acciones = [], [], [], []
    # En el orden de la entidad, para que las opciones del menú queden ordenadas.
    for campo in (c for c in entrada.campos if c.nombre in pedidos):
        texto = campo.tipo == "str"
        columna = f"{campo.nombre}_id" if campo.tipo == relaciones.TIPO else campo.nombre
        funciones.append(
            _FUNCION_BUSQUEDA.format(
                c=campo.nombre,
                doc=f"Los registros cuyo {campo.nombre} contiene el texto (sin distinguir mayúsculas)." if texto else f"Los registros con ese {columna}.",
                tabla=entrada.nombre.plural,
                columna=columna,
                operador="LIKE" if texto else "=",
                # LIKE con % antes y después: "contiene". SQLite no distingue mayúsculas en LIKE.
                parametro='f"%{valor}%"' if texto else "valor",
            )
        )
        tipo = "str" if texto else "float" if campo.tipo == "float" else "int"
        funciones_menu.append(_MENU_BUSQUEDA.format(c=campo.nombre, titulo=campo.titulo, tipo=tipo, entidad=sol.nombre.snake))
        # El número sale del orden del campo en la entidad (5 el primero, 6 el segundo...):
        # no depende de qué otras búsquedas haya, y no se repite.
        numero = 5 + list(campos).index(campo.nombre)
        opciones.append(f'print("{numero}. Buscar por {campo.nombre}")')
        acciones += [f'elif opcion == "{numero}":', f"    buscar_por_{campo.nombre}()"]
    return {
        # Dos líneas en blanco entre funciones, como pide la guía de estilo de Python (PEP 8).
        "funciones_entidad": "\n\n\n".join(f.strip("\n") for f in funciones),
        "funciones_menu": "\n\n\n".join(f.strip("\n") for f in funciones_menu),
        "opciones_menu": "\n".join(opciones),
        "acciones_menu": "\n".join(acciones),
    }


BUSQUEDA = Pieza(
    clave="busqueda",
    lectura=(
        ('entidades/@@nombre@@.py', 'buscar_por_...(): la consulta, al final del archivo'),
        ('menus/menu_@@nombre@@.py', 'la opción nueva del menú y la función que pide qué buscar'),
    ),
    titulo="Búsqueda",
    descripcion="buscar por un campo en una entidad que ya existe (función y opción del menú)",
    ejemplo="articulo nombre",
    preparar=("entidad articulo nombre:str precio:float",),
    formas=("snake",),
    usa_campos=True,
    define_campos=False,
    usa_existente=True,
    contexto=_contexto_busqueda,
    marcadores={
        "funciones_entidad": "buscar_por_<campo>(valor) para entidades/<nombre>.py",
        "funciones_menu": "la función del menú que pide el valor y muestra los resultados",
        "opciones_menu": 'el print de cada opción nueva: print("5. Buscar por nombre")',
        "acciones_menu": 'el elif de cada opción nueva: elif opcion == "5":',
    },
    inserciones=(
        Insercion("entidades/@@nombre@@.py", "\n\n@@funciones_entidad@@", descripcion="buscar_por_... (al final)"),
        Insercion(
            "menus/menu_@@nombre@@.py",
            "@@opciones_menu@@",
            marcador="opciones",
            descripcion="la opción en el menú",
            ubicacion='en mostrar_menu(), antes de print("0. Volver")',
        ),
        Insercion(
            "menus/menu_@@nombre@@.py",
            "@@acciones_menu@@",
            marcador="acciones",
            descripcion="qué hace la opción",
            ubicacion='en mostrar_menu(), antes de elif opcion == "0":',
        ),
        Insercion("menus/menu_@@nombre@@.py", "\n\n@@funciones_menu@@", descripcion="la función del menú (al final)"),
    ),
    siguiente_paso=["python main.py"],
)

STACK = Stack(
    clave="python",
    titulo="Python + SQLite",
    senal="main.py y db.py",
    detectar=_detectar,
    tipos=TIPOS,
    piezas={"entidad": ENTIDAD, "menu": MENU, "busqueda": BUSQUEDA},
    ejemplo_proyecto="mi-tienda",
    siguiente_paso_proyecto=["cd @@carpeta@@", "python main.py"],
    validar_nombre=_validar_nombre,
)
